# Resumen de la Arquitectura

La solución propuesta integra diversos servicios de WS para cubrir las necesidades de procesamiento, almacenamiento y monitoreo.

## Servicios de arquitectura a utilizar

- **EC2**: Procesamiento por lotes de logs de seguridad, permitiendo un análisis eficiente de grandes volúmenes de datos.
- **RDS**: Almacenamiento seguro y escalable de eventos de seguridad detectados durante el procesamiento de los logs.
- **AWS Lambda**: Detección de anomalías en tiempo real.
- **Docker**: Contenerización de algoritmos de detección de amenazas desarrollados en Python.
- **CloudWatch**: Monitoreo de logs y eventos de seguridad.
- **S3**: Almacenamiento de logs de seguridad y eventos de seguridad detectados.
- **Amazon Kinesis**: Procesamiento de streams de logs en tiempo real.
- **IAM**: Gestión de roles y usuarios.
