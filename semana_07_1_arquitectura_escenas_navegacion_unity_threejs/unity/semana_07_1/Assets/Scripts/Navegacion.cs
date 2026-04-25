using UnityEngine;
using UnityEngine.SceneManagement;

public class Navegacion : MonoBehaviour
{
    public void IrAJuego()
    {
        SceneManager.LoadScene("Juego");
    }

    public void IrACreditos()
    {
        SceneManager.LoadScene("Creditos");
    }

    public void IrAMenu()
    {
        SceneManager.LoadScene("Menu");
    }

    public void Salir()
    {
        Application.Quit();
    }
}