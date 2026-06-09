using UnityEngine;

[RequireComponent(typeof(LineRenderer))]
public class RobotNavegacion : MonoBehaviour
{
    [Header("Parámetros de Navegación")]
    public float speed = 3f;
    public float rotationSpeed = 120f; // Aumentamos un poco la velocidad de giro para escapar de esquinas
    public float rayDistance = 4f;

    [Header("Meta")]
    public Transform goal;

    [Header("Configuración de Trayectoria")]
    public float updateDistance = 0.5f;
    private LineRenderer lineRenderer;
    private int positionCount = 0;
    private Vector3 lastPosition;

    // Variable para recordar hacia dónde estábamos evadiendo
    private float evasionDirection = 1f; // 1 = Derecha, -1 = Izquierda

    void Start()
    {
        lineRenderer = GetComponent<LineRenderer>();
        lineRenderer.startWidth = 0.1f;
        lineRenderer.endWidth = 0.1f;
        lineRenderer.material = new Material(Shader.Find("Sprites/Default"));
        lineRenderer.startColor = Color.blue;
        lineRenderer.endColor = Color.blue;
        
        lastPosition = transform.position;
        UpdateTrajectory();
    }

    void Update()
    {
        // 1. Condición de victoria
        if (goal != null && Vector3.Distance(transform.position, goal.position) < 1.5f)
        {
            Debug.Log("¡Meta alcanzada!");
            return;
        }

        // 2. Definir los tres ángulos de visión (Sensores)
        Vector3 forward = transform.forward;
        Vector3 left45 = Quaternion.Euler(0, -45, 0) * transform.forward;
        Vector3 right45 = Quaternion.Euler(0, 45, 0) * transform.forward;

        // 3. Lanzar los rayos y guardar si golpearon algo (y a qué distancia)
        bool hitForward = Physics.Raycast(transform.position, forward, out RaycastHit fHit, rayDistance);
        bool hitLeft = Physics.Raycast(transform.position, left45, out RaycastHit lHit, rayDistance);
        bool hitRight = Physics.Raycast(transform.position, right45, out RaycastHit rHit, rayDistance);

        // Dibujar los rayos en la escena para visualizar las decisiones
        Debug.DrawRay(transform.position, forward * rayDistance, hitForward ? Color.red : Color.green);
        Debug.DrawRay(transform.position, left45 * rayDistance, hitLeft ? Color.yellow : Color.cyan);
        Debug.DrawRay(transform.position, right45 * rayDistance, hitRight ? Color.yellow : Color.cyan);

        // 4. Lógica de Navegación y Evasión
        if (hitForward)
        {
            // ¡Obstáculo al frente! Decidir hacia dónde es mejor girar
            if (hitRight && !hitLeft) {
                evasionDirection = -1f; // Derecha bloqueada, girar Izquierda
            } 
            else if (hitLeft && !hitRight) {
                evasionDirection = 1f;  // Izquierda bloqueada, girar Derecha
            } 
            else if (hitLeft && hitRight) {
                // Ambos lados bloqueados (ej. un túnel muy estrecho o esquina). 
                // Gira hacia el lado donde el obstáculo esté más lejos.
                if (lHit.distance > rHit.distance) evasionDirection = -1f;
                else evasionDirection = 1f;
            }
            // Si ninguno de los lados detecta obstáculo, mantiene la dirección de evasión actual

            // Ejecutar el giro
            transform.Rotate(0, rotationSpeed * evasionDirection * Time.deltaTime, 0);
        }
        else
        {
            // ¡Camino libre al frente! 
            // Intentar mirar hacia la meta de forma inteligente
            if (goal != null)
            {
                // Calcular vector dirección hacia la meta
                Vector3 directionToGoal = (goal.position - transform.position).normalized;
                directionToGoal.y = 0; // Ignorar la altura para que el robot no intente mirar hacia arriba/abajo

                // Rotar suavemente hacia la meta
                Quaternion targetRotation = Quaternion.LookRotation(directionToGoal);
                transform.rotation = Quaternion.RotateTowards(transform.rotation, targetRotation, (rotationSpeed * 0.5f) * Time.deltaTime);
            }

            // Avanzar siempre
            transform.Translate(Vector3.forward * Time.deltaTime * speed);
        }

        // 5. Actualizar la línea de trayectoria
        if (Vector3.Distance(transform.position, lastPosition) > updateDistance)
        {
            lastPosition = transform.position;
            UpdateTrajectory();
        }
    }

    void UpdateTrajectory()
    {
        positionCount++;
        lineRenderer.positionCount = positionCount;
        Vector3 groundPosition = new Vector3(transform.position.x, 0.1f, transform.position.z);
        lineRenderer.SetPosition(positionCount - 1, groundPosition);
    }
}