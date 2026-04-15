using UnityEngine;

public class ColisionParticulas : MonoBehaviour
{
    [Header("Efectos Visuales y Sonoros")]
    [Tooltip("Arrastra aquí el Prefab del sistema de partículas")]
    public GameObject particulasPrefab; 
    
    [Tooltip("Opcional: Arrastra un clip de audio para el impacto")]
    public AudioClip sonidoColision;    
    
    private AudioSource audioSource;

    private void Start()
    {
        // Añadimos un AudioSource dinámicamente si hay un sonido configurado
        if (sonidoColision != null)
        {
            audioSource = gameObject.AddComponent<AudioSource>();
            audioSource.playOnAwake = false;
            audioSource.spatialBlend = 1f; // Sonido 3D
        }
    }

    private void OnCollisionEnter(Collision collision)
    {
        // Solo reproducir efectos si el impacto tiene suficiente fuerza (evita partículas continuas al descansar en el suelo)
        if (collision.relativeVelocity.magnitude > 1.5f)
        {
            if (particulasPrefab != null)
            {
                // Obtenemos el punto de contacto exacto
                Vector3 puntoImpacto = collision.contacts[0].point;
                // Instanciamos el Prefab en ese punto orientado hacia arriba
                Instantiate(particulasPrefab, puntoImpacto, Quaternion.LookRotation(collision.contacts[0].normal));
            }

            if (audioSource != null && sonidoColision != null)
            {
                // Reproducimos el sonido sin interrumpir colisiones simultáneas
                audioSource.PlayOneShot(sonidoColision);
            }
        }
    }
}