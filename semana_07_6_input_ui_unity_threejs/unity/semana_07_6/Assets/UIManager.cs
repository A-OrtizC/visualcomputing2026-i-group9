using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class UIManager : MonoBehaviour
{
    public Transform player;
    public TMP_Text coordsText;
    public Slider slider;

    void Update()
    {
        // Coordenadas
        coordsText.text =
            "X: " + player.position.x.ToString("F1") +
            " Z: " + player.position.z.ToString("F1");

        // Barra dinámica
        slider.value = Mathf.PingPong(Time.time, 1f);
    }

    public void ResetPlayer()
    {
        player.position = new Vector3(0, 1, 0);
    }
}