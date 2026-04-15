using UnityEngine;

public class SoundController : MonoBehaviour
{
    public AudioSource audioSource;

    public AudioClip walkClip1;
    public AudioClip walkClip2;
    public AudioClip waveClip;

    public void PlayFootstep1()
    {
        audioSource.PlayOneShot(walkClip1);
    }

    public void PlayFootstep2()
    {
        audioSource.PlayOneShot(walkClip2);
    }

    public void PlayWaveSound()
    {
        audioSource.PlayOneShot(waveClip);
    }
}