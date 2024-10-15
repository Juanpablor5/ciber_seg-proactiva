# EC2

## ¿Qué es?

Amazon EC2 (Elastic Compute Cloud) es un servicio de Amazon Web Services (AWS) que proporciona capacidad de cómputo elástica en la nube. Permite a los usuarios lanzar y gestionar instancias de servidores virtuales de forma flexible, según las necesidades de procesamiento de su aplicación.

En este caso, EC2 se utilizará para el procesamiento de logs de seguridad por lotes. Se elegirán instancias de acuerdo con la demanda, lo cual permite ajustar los recursos a las necesidades en tiempo real, optimizando costos y rendimiento.

![](../../assets/EC2/EC2_1.png)

### ¿Por qué es necesario?

El uso de EC2 es esencial para manejar grandes volúmenes de datos en forma de logs, dado que permite:

Escalabilidad dinámica: Las instancias EC2 se pueden escalar vertical y horizontalmente según el volumen de logs a procesar, lo que garantiza que el sistema pueda responder adecuadamente tanto a picos de demanda como a cargas más reducidas.

Optimización de costos: Al ser un servicio pago por uso, solo se incurre en costos por los recursos efectivamente utilizados. Esto evita los costos asociados a la compra y mantenimiento de servidores físicos.

Flexibilidad y personalización: EC2 permite seleccionar el tipo y configuración de instancia que mejor se adapte a las necesidades del negocio, así como instalar y ejecutar cualquier software necesario para el procesamiento de los logs.

## Estimación de costos

Para estimar los costos asociados al uso de instancias EC2, utilizaremos la calculadora de AWS y consideraremos valores estimados:

1. **Región**: US East (Ohio)

2. **Tipo de instancia EC2**

Las instancias c5.large están diseñadas para aplicaciones que requieren un alto rendimiento de procesamiento de CPU. Aquí algunos factores a considerar:

Volumen de Datos: Si el volumen de logs es alto, podrías necesitar varias instancias para manejar la carga. Un punto de partida razonable sería comenzar con 2 a 4 instancias y ajustar según las necesidades.
Demanda de Procesamiento: Considera cuántos registros por segundo necesitas procesar y si el procesamiento requiere de CPU intensiva. Las instancias c5.large cuentan con 2 vCPUs y 4 GB de memoria, ideales para cargas moderadas de procesamiento.
Alta Disponibilidad: Para garantizar disponibilidad continua, podría ser útil usar al menos 2 instancias para balanceo de carga.

   | Concepto       | Configuración                 | Comentario                            |
   | -------------- | ----------------------------- | ------------------------------------- |
   | Instancia      | `c5.large` (2 vCPU, 4 GB RAM) | Suficiente para el procesamiento logs |
   | Costo por hora | Aproximadamente $0.042        | Por instancia                         |

3. **Número de instancias**:

   | Concepto | Configuración | Comentario                                   |
   | -------- | ------------- | -------------------------------------------- |
   | Cantidad | 2 instancias  | Para alta disponibilidad y balanceo de carga |

4. **Horas mensuales de operación**:

   | Concepto       | Configuración | Comentario                              |
   | -------------- | ------------- | --------------------------------------- |
   | Total de horas | 730 horas     | Asumiendo operación 24/7 durante un mes |

5. **Cálculo del costo de las instancias EC2**:

   | Concepto                   | Cálculo               | Costo  |
   | -------------------------- | --------------------- | ------ |
   | Costo por instancia        | $0.042 x 730 horas    | $30.66 |
   | Costo total (2 instancias) | $30.66 x 2 instancias | $61.32 |

6. **Almacenamiento EBS**:

   | Concepto         | Configuración                  | Costo  |
   | ---------------- | ------------------------------ | ------ |
   | Tipo de volumen  | General Purpose SSD (gp2)      |        |
   | Tamaño           | 50 GB por instancia            |        |
   | Costo por GB/mes | $0.10                          |        |
   | Costo total      | 50 GB x $0.10 x 2 instancias   | $10.00 |

7. **Datos de transferencia**:

   - **Asunción**: El tráfico de salida está dentro del nivel gratuito o es mínimo, por lo que no se considera en el cálculo.

**Con la información anterior los costos son:**

| Concepto                              | Costo Mensual |
| ------------------------------------- | ------------- |
| Costo de instancias EC2 (mensual)     | $61.32        |
| Costo de almacenamiento EBS (mensual) | $10.00        |
| **Total**                             | **$71.32**    |


## Pasos detallados para despliegue para EC2

1. **Configurar instancia EC2**:
   - Iniciar sesión en AWS Management Console y navegar a EC2.
 
![](../../assets/EC2/ec2_2.png)   

   - Hacer clic en "Launch Instance" para iniciar el proceso de configuración.

![](../../assets/EC2/ec2_3.png)   

   - Escoger el tipo de instancia, en este caso, c5.large (o cualquier tipo según los requisitos)

![](../../assets/EC2/ec2_4.png) 

   - Configurar las reglas de seguridad, habilitando el acceso SSH (puerto 22) y cualquier otro puerto necesario.

![](../../assets/EC2/ec2_5.png)

   - Hacer clic en "Launch" y seleccionar crear un par de claves (key pair) para conectarse a la instancia.

![](../../assets/EC2/ec2_6.png)   

2. **Instalar software necesario en la instancia**:
   - Conectar a la instancia EC2 mediante SSH.

     ```bash
     ssh -i "nombre_de_tu_llave.pem" ec2-user@tu_direccion_ip_publica
     ```

   - Actualizar el sistema operativo e instalar las herramientas necesarias, como Docker, Python y otros paquetes requeridos para el procesamiento de los logs.
     
     ```bash
     # Actualizar el sistema operativo
     sudo yum update -y
     
     # Instalar Docker
     sudo amazon-linux-extras install docker
     sudo service docker start
     sudo usermod -a -G docker ec2-user
     
     # Instalar Python
     sudo yum install python3 -y
     ```

3. **Desplegar contenedores Docker en EC2**:

   - Instalar Docker en la instancia EC2.
   - Crear o descargar la imagen Docker con los algoritmos de detección desarrollados en Python.
   - Ejecutar los contenedores con los algoritmos y asegurarse de que estén corriendo correctamente.

4. **Configurar monitoreo y alertas**:

   - Utilizar AWS CloudWatch para monitorizar la instancia EC2 y configurar métricas clave como uso de CPU, memoria y disco.
   - Configurar alarmas para recibir notificaciones si se superan ciertos umbrales, garantizando la operatividad de la instancia.

