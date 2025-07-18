## Common Issues and Solutions

### 1. Pod Fails to Start
```bash
# Check pod logs
kubectl logs -n llm-deployment deployment/llm-deployment

# Check pod events
kubectl describe pod -n llm-deployment -l app=llm-api

# Check resource constraints
kubectl top pods -n llm-deployment
```

### 2. Model Loading Issues
```bash
# Check if model cache is working
kubectl exec -n llm-deployment -it deployment/llm-deployment -- ls -la /root/.cache/huggingface

# Check network connectivity
kubectl exec -n llm-deployment -it deployment/llm-deployment -- curl -I https://huggingface.co
```

### 3. Load Balancer Issues
```bash
# Check ALB controller logs
kubectl logs -n kube-system deployment/aws-load-balancer-controller

# Check ingress status
kubectl describe ingress -n llm-deployment llm-ingress

# Check security groups
aws ec2 describe-security-groups --group-ids $(kubectl get ingress -n llm-deployment llm-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
```

### 4. Performance Issues
```bash
# Check HPA status
kubectl get hpa -n llm-deployment

# Check node resources
kubectl top nodes

# Check pod resource usage
kubectl top pods -n llm-deployment
```

### 5. Networking Issues
```bash
# Check network policies
kubectl get networkpolicies -n llm-deployment

# Test internal connectivity
kubectl exec -n llm-deployment -it deployment/llm-deployment -- curl llm-service

# Check DNS resolution
kubectl exec -n llm-deployment -it deployment/llm-deployment -- nslookup llm-service
```
