// MovimientoLimitado.cs
// Taller 63 - Objeto controlable dentro de los límites de la cámara
// Versión adaptada al NUEVO Input System de Unity (com.unity.inputsystem)
//
// Mueve un objeto con las teclas WASD o flechas mientras lo mantiene
// siempre visible dentro del campo de visión de la cámara principal.
//
// REQUISITO: el paquete "Input System" debe estar instalado en el proyecto
// (Window → Package Manager → buscar "Input System" → Install).
// Si tu proyecto ya usa el nuevo Input System (como en tu caso), no necesitas
// instalar nada más: este script funciona directamente.
//
// INSTRUCCIONES DE USO:
//  - Arrastra este script sobre el objeto que quieras mover (ej. "JugadorCubo").
//  - No requiere configuración adicional: detecta la cámara principal (Main Camera)
//    automáticamente y calcula los límites visibles según su posición/ángulo.

using UnityEngine;
using UnityEngine.InputSystem;

public class MovimientoLimitado : MonoBehaviour
{
    [Header("Movimiento")]
    [Tooltip("Velocidad de desplazamiento del objeto.")]
    public float velocidad = 5f;

    [Header("Límites de cámara")]
    [Tooltip("Distancia (en el eje Z) a la que se calculan los límites visibles, " +
             "normalmente la distancia entre la cámara y el plano donde se mueve el objeto.")]
    public float distanciaAlPlano = 10f;

    [Tooltip("Margen extra para que el objeto no toque justo el borde de la pantalla.")]
    public float margen = 0.5f;

    private Camera camaraPrincipal;
    private float alturaFija; // mantiene constante la altura (eje Y) del objeto

    void Start()
    {
        camaraPrincipal = Camera.main;

        if (camaraPrincipal == null)
        {
            Debug.LogError("[MovimientoLimitado] No se encontró ninguna cámara con tag 'MainCamera'. " +
                            "Asegúrate de que tu cámara tenga ese tag asignado.");
        }

        alturaFija = transform.position.y;
    }

    void Update()
    {
        if (camaraPrincipal == null) return;

        // ── Lectura de input con el NUEVO Input System ──
        // Keyboard.current nos da acceso directo a las teclas sin necesitar
        // un Input Action Asset configurado manualmente.
        Vector2 input = Vector2.zero;

        if (Keyboard.current != null)
        {
            if (Keyboard.current.aKey.isPressed || Keyboard.current.leftArrowKey.isPressed)
                input.x -= 1f;
            if (Keyboard.current.dKey.isPressed || Keyboard.current.rightArrowKey.isPressed)
                input.x += 1f;
            if (Keyboard.current.sKey.isPressed || Keyboard.current.downArrowKey.isPressed)
                input.y -= 1f;
            if (Keyboard.current.wKey.isPressed || Keyboard.current.upArrowKey.isPressed)
                input.y += 1f;
        }

        Vector3 movimiento = new Vector3(input.x, 0f, input.y) * velocidad * Time.deltaTime;
        Vector3 nuevaPosicion = transform.position + movimiento;

        // ── Calcular límites visibles de la cámara en este instante ──
        Vector3 limites = CalcularLimitesVisibles();

        nuevaPosicion.x = Mathf.Clamp(nuevaPosicion.x, -limites.x, limites.x);
        nuevaPosicion.z = Mathf.Clamp(nuevaPosicion.z, -limites.z, limites.z);
        nuevaPosicion.y = alturaFija; // el objeto no cambia de altura

        transform.position = nuevaPosicion;
    }

    /// <summary>
    /// Calcula el ancho y profundidad visibles desde la cámara a una distancia dada,
    /// usando el FOV (campo de visión) y el aspecto de pantalla.
    /// Esto evita que el objeto se salga de cuadro sin importar la resolución.
    /// </summary>
    Vector3 CalcularLimitesVisibles()
    {
        float distancia = distanciaAlPlano;

        // Altura visible a esa distancia, según el FOV vertical de la cámara
        float alturaVisible = 2f * distancia * Mathf.Tan(camaraPrincipal.fieldOfView * 0.5f * Mathf.Deg2Rad);
        float anchoVisible = alturaVisible * camaraPrincipal.aspect;

        float limiteX = (anchoVisible / 2f) - margen;
        float limiteZ = (alturaVisible / 2f) - margen;

        return new Vector3(Mathf.Max(limiteX, 0f), 0f, Mathf.Max(limiteZ, 0f));
    }
}