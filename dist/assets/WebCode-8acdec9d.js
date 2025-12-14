import"./base-023a9467.js";import{E as c}from"./card-7b9566ef.js";import{_ as r}from"./CodeEditor-652116f5.js";import{r as t,o as n,a as l,c as e,w as a}from"./index-ab9da3ee.js";import"./_commonjsHelpers-de833af9.js";const p={class:"flex flex-col px-[4rem] py-[2rem] space-y-[1rem]"},k={__name:"WebCode",setup(m){const s=t(`apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    weave.io/platform: "true"
  creationTimestamp: "2022-06-08T07:30:32Z"
  generation: 1
  labels:
    weave.io/app: app-demo
    weave.io/creator: admin
    weave.io/platform: "true"
  name: app-tets
  namespace: default
  resourceVersion: "11192156"
  uid: 84206da4-4386-41fd-a70d-498ca4f56f9f
spec:
  progressDeadlineSeconds: 600
  replicas: 1
  revisionHistoryLimit: 10
  selector:
    matchLabels:
      weave.io/app: app-demo
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      creationTimestamp: null
      labels:
        weave.io/app: app-demo
    spec:
      containers:
      - image: nginx
        imagePullPolicy: Always
        name: nginx
        terminationMessagePolicy: File
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext: {}
      terminationGracePeriodSeconds: 30
`),i=t(`
#log<info>log#2021-08-26 15:07:09: job is success#log<info>log#
#log<warning>log#2021-08-26 15:07:09: job is success#log<warning>log#
#log<error>log#2021-08-26 15:07:09: job is error#log<error>log#

2022/05/30 07:21:55 [notice] 1#1: using the "epoll" event method
2022/05/30 07:21:55 [notice] 1#1: nginx/1.21.6
2022/05/30 07:21:55 [notice] 1#1: built by gcc 10.2.1
2022/05/30 07:21:55 [notice] 1#1: OS: Linux 5.3.18-150300
2022/05/30 07:21:55 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
2022/05/30 07:21:55 [notice] 1#1: start worker processes
2022/05/30 07:21:55 [notice] 1#1: start worker process 37
2022/05/30 07:21:55 [notice] 1#1: start worker process 38
2022/05/30 07:21:55 [notice] 1#1: start worker process 39
2022/05/30 07:21:55 [notice] 1#1: start worker process 40
2022/05/30 07:21:55 [notice] 1#1: start worker process 41
2022/05/30 07:21:55 [notice] 1#1: start worker process 42
2022/05/30 07:21:55 [notice] 1#1: start worker process 43
2022/05/30 07:21:55 [notice] 1#1: start worker process 44
2022/05/30 07:21:55 [notice] 1#1: start worker process 45
2022/05/30 07:21:55 [notice] 1#1: start worker process 46
2022/05/30 07:21:55 [notice] 1#1: start worker process 47
2022/05/30 07:21:55 [notice] 1#1: start worker process 48
2022/05/30 07:21:55 [notice] 1#1: start worker process 49
2022/05/30 07:21:55 [notice] 1#1: start worker process 50
`);return(d,g)=>{const o=c;return n(),l("div",p,[e(o,{header:"Yaml Editor"},{default:a(()=>[e(r,{height:"60vh",value:s.value},null,8,["value"])]),_:1}),e(o,{header:"Log view"},{default:a(()=>[e(r,{height:"60vh",mode:"log",readOnly:"",light:"",value:i.value},null,8,["value"])]),_:1})])}}};export{k as default};
