using System;
using UnityEngine;
using UnityEngine.Video;

public class PanoramaLoader : MonoBehaviour {
	Renderer rend;
	VideoPlayer vp;
	public float sensitivity = 1;

	private void Start() {
		rend = GetComponent<Renderer>();
		vp = GetComponent<VideoPlayer>();
	}

	public void ShowVideo(VideoClip clip) {
		Debug.Log("Loading video " +  clip.name);
		vp.clip = clip;

		vp.Play();
    }

	public void ShowStatic(Texture2D tex) {
		Debug.Log("Loading photo " + tex.name);
		//frenar video para evitar conflictos
		if(vp.isPlaying)
			vp.Stop();
        rend.material.mainTexture = tex;
	}
}
