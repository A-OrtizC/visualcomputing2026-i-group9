using UnityEngine;

public class UIController : MonoBehaviour
{
    public Player player;

    // 📋 Dropdown
    public void ChangeAnimation(int index)
    {

        switch (index)
        {
            case 0:
                player.PlayAnimation("idle");
                player.GetComponent<Animator>().SetFloat("Speed", 0f);
                break;
            case 1:
                player.PlayAnimation("walk");
                player.GetComponent<Animator>().SetFloat("Speed", 0.4f);
                break;
            case 2:
                player.PlayAnimation("run");
                player.GetComponent<Animator>().SetFloat("Speed", 1f);
                break;
            case 3:
                player.PlayAnimation("waving");
                player.GetComponent<Animator>().SetFloat("Speed", 0f);
                break;
        }
    }

    // ⏸️ Pausar
    public void Pause()
    {
        player.PauseAnimation();
    }

    // ▶️ Reanudar animación (sin devolver control)
    public void ResumeAnim()
    {
        player.ResumeAnimation();
    }

    // 🎮 Volver a control del jugador
    public void ResumePlayerControl()
    {
        player.ResumePlayer();
    }

    // 🔄 Reiniciar animación actual
    public void Restart()
    {
        player.RestartAnimation();
    }
}