using UnityEngine;

public sealed class ControladorBrazo : MonoBehaviour
{
    [Header("Articulaciones")]
    public Transform hombro;
    public Transform codo;

    [Header("Pinza")]
    public Transform dedoIzq;
    public Transform dedoDer;
    public Transform puntaDeLaPinza; // Arrastra aquí el objeto al final de la pinza

    [Header("Controles")]
    [Range(-90f, 90f)] public float anguloHombro;
    [Range(-120f, 120f)] public float anguloCodo;
    [Range(0f, 0.05f)] public float aperturaPinza;
    public bool animacionAutomatica = false;

    private Vector3 ultimaPosicion;

    void Start() 
    {
        // Inicializamos la posición para el dibujo de la trayectoria
        if (puntaDeLaPinza != null)
        {
            ultimaPosicion = puntaDeLaPinza.position;
        }
    }

    void Update()
    {
        // 1. Lógica de Animación Automática (Opcional)
        if (animacionAutomatica)
        {
            float t = Time.time;
            anguloHombro = Mathf.Sin(t) * 45f;
            anguloCodo = Mathf.Cos(t * 1.2f) * 60f;
        }

        // 2. Aplicamos la Cinemática Directa (FK)
        // Las rotaciones locales se heredan por la jerarquía de Unity
        if (hombro != null) hombro.localRotation = Quaternion.Euler(0, 0, anguloHombro);
        if (codo != null) codo.localRotation = Quaternion.Euler(0, 0, anguloCodo);

        // 3. Control de la pinza (movimiento lineal de los dedos)
        if (dedoIzq != null) dedoIzq.localPosition = new Vector3(-aperturaPinza, 0.1f, 0);
        if (dedoDer != null) dedoDer.localPosition = new Vector3(aperturaPinza, 0.1f, 0);

        // 4. Visualización de la trayectoria con Debug.DrawLine
        if (puntaDeLaPinza != null)
        {
            // Dibuja una línea roja que dura 2 segundos en la Scene View
            Debug.DrawLine(ultimaPosicion, puntaDeLaPinza.position, Color.red, 2f);
            
            // Actualizamos la posición para el siguiente frame
            ultimaPosicion = puntaDeLaPinza.position;
        }
    }
}