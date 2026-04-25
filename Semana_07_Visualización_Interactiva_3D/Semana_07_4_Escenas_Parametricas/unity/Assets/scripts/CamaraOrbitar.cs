using UnityEngine;

public partial class CamaraOrbitar : MonoBehaviour
{
    public Transform centro; // El objeto _Generador
    public float velocidadGiro = 20f;
    public float distancia = 10f;
    public float altura = 5f;

    void Update()
    {
        if (centro != null)
        {
            // Calculamos la posición en un círculo usando el tiempo
            float angulo = Time.time * velocidadGiro;
            Quaternion rotacion = Quaternion.Euler(0, angulo, 0);
            Vector3 posicionRelativa = rotacion * new Vector3(0, 0, -distancia);

            // Aplicamos posición y altura
            transform.position = centro.position + posicionRelativa + Vector3.up * altura;

            // Hacemos que la cámara siempre mire al centro
            transform.LookAt(centro.position);
        }
    }
}