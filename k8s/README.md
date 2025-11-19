# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying HDHomeRun Scanner.

## Quick Start

```bash
# 1. Create configuration
kubectl apply -f configmap.yaml

# 2. Create secrets
cp secret.yaml.example secret.yaml
nano secret.yaml  # Add your values
kubectl apply -f secret.yaml

# 3. Create storage
kubectl apply -f pvc.yaml

# 4. Deploy CronJobs
kubectl apply -f cronjob.yaml

# 5. Verify
kubectl get pods -l app=hdhr-scanner
kubectl get cronjobs
```

## Files

- `configmap.yaml` - Application configuration
- `secret.yaml.example` - Template for secrets (copy to secret.yaml)
- `pvc.yaml` - Persistent volume claims for output and logs
- `cronjob.yaml` - Scheduled scan jobs (daily and weekly)

## Configuration

### Secrets

**Never commit secret.yaml to version control!**

Create from template:
```bash
cp secret.yaml.example secret.yaml
nano secret.yaml
```

Or create from command line:
```bash
kubectl create secret generic hdhr-scanner-secrets \
  --from-literal=OPENAI_API_KEY='your-key' \
  --from-literal=HDHR_DEVICE_ID='12345678'
```

### ConfigMap

Edit `configmap.yaml` to change:
- Log level
- Timeouts
- Default settings

Apply changes:
```bash
kubectl apply -f configmap.yaml
```

## Scheduling

Two CronJobs are included:

1. **hdhr-scanner-daily**: Runs daily at 3:00 AM UTC
2. **hdhr-scanner-weekly**: Runs weekly (Sundays) at 2:00 AM UTC

### Customize Schedule

Edit `cronjob.yaml` and modify the `schedule` field:
```yaml
spec:
  schedule: "0 3 * * *"  # Cron format: minute hour day month day-of-week
```

### Manual Trigger

Create a one-time job from CronJob:
```bash
kubectl create job --from=cronjob/hdhr-scanner-daily manual-scan-$(date +%s)
```

## Monitoring

### View Logs

```bash
# Get recent pod name
POD=$(kubectl get pods -l app=hdhr-scanner --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')

# View logs
kubectl logs $POD

# Follow logs
kubectl logs -f $POD
```

### Check Status

```bash
# CronJobs
kubectl get cronjobs

# Recent jobs
kubectl get jobs --sort-by=.metadata.creationTimestamp

# Pods
kubectl get pods -l app=hdhr-scanner
```

### Describe Resources

```bash
kubectl describe cronjob hdhr-scanner-daily
kubectl describe pod <pod-name>
```

## Storage

Two PersistentVolumeClaims are created:

1. **hdhr-scanner-output** (10 GB) - Scan results
2. **hdhr-scanner-logs** (5 GB) - Application logs

### Access Storage

Create a debug pod:
```bash
kubectl run -it --rm debug --image=busybox \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "debug",
      "image": "busybox",
      "stdin": true,
      "tty": true,
      "volumeMounts": [{
        "name": "output",
        "mountPath": "/output"
      }]
    }],
    "volumes": [{
      "name": "output",
      "persistentVolumeClaim": {
        "claimName": "hdhr-scanner-output"
      }
    }]
  }
}'

# Inside pod:
ls /output
```

### Backup Storage

```bash
# Export data
kubectl cp <pod-name>:/app/output ./backup-output

# Or use a backup job
kubectl create job backup --image=ubuntu -- \
  tar czf /backup/output.tar.gz /app/output
```

## Networking

The scanner requires **host networking** to discover HDHomeRun devices via UDP broadcast.

This is configured in the CronJob:
```yaml
spec:
  template:
    spec:
      hostNetwork: true
      dnsPolicy: ClusterFirstWithHostNet
```

**Important:** This means the pod shares the node's network namespace. Ensure your cluster nodes are on the same network as HDHomeRun devices.

## Security

Security context is configured for non-root execution:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
```

### Recommendations

1. Use a dedicated namespace:
   ```bash
   kubectl create namespace hdhr-scanner
   kubectl apply -f . -n hdhr-scanner
   ```

2. Apply NetworkPolicies (if not using hostNetwork)

3. Enable Pod Security Standards:
   ```bash
   kubectl label namespace hdhr-scanner \
     pod-security.kubernetes.io/enforce=baseline
   ```

4. Use RBAC to restrict access:
   ```yaml
   apiVersion: rbac.authorization.k8s.io/v1
   kind: Role
   metadata:
     name: hdhr-scanner-role
   rules:
   - apiGroups: [""]
     resources: ["pods", "configmaps", "secrets"]
     verbs: ["get", "list"]
   ```

## Resource Management

Resource limits are configured per container:
```yaml
resources:
  limits:
    cpu: "1000m"      # 1 CPU core
    memory: "512Mi"   # 512 MB RAM
  requests:
    cpu: "500m"       # 0.5 CPU core
    memory: "256Mi"   # 256 MB RAM
```

### Adjust Resources

Edit `cronjob.yaml` to increase/decrease based on your needs.

## Troubleshooting

### CronJob Not Running

```bash
# Check CronJob status
kubectl get cronjob hdhr-scanner-daily

# Check recent jobs
kubectl get jobs

# Check CronJob events
kubectl describe cronjob hdhr-scanner-daily
```

### Pod Failures

```bash
# Get pod status
kubectl get pods -l app=hdhr-scanner

# View logs
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>

# Check secrets
kubectl get secrets hdhr-scanner-secrets -o yaml
```

### Network Issues

```bash
# Exec into pod
kubectl exec -it <pod-name> -- bash

# Test hdhomerun_config
hdhomerun_config discover

# Check network
ip addr
route -n
```

### Storage Issues

```bash
# Check PVCs
kubectl get pvc

# Describe PVC
kubectl describe pvc hdhr-scanner-output

# Check disk usage
kubectl exec <pod-name> -- df -h /app/output
```

## Cleanup

Remove all resources:
```bash
kubectl delete -f .

# Or individual resources
kubectl delete cronjob hdhr-scanner-daily hdhr-scanner-weekly
kubectl delete pvc hdhr-scanner-output hdhr-scanner-logs
kubectl delete configmap hdhr-scanner-config
kubectl delete secret hdhr-scanner-secrets
```

## See Also

- [DEVOPS_QUICKSTART.md](../DEVOPS_QUICKSTART.md) - Quick deployment guide
- [DEPLOYMENT.md](../DEPLOYMENT.md) - Comprehensive deployment documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/)
