using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Video;
public class InitDropdown : MonoBehaviour {
	[SerializeField] private PanoramaLoader loader;

	private Texture2D[] textures;
	private VideoClip[] clips;
	private List<string> names;
	private TMP_Dropdown drop;

	void Start() {
		drop = GetComponent<TMP_Dropdown>();
		drop.ClearOptions();

		//Cargar imagenes y videos
		textures = Resources.LoadAll<Texture2D>("panorama");
		clips = Resources.LoadAll<VideoClip>("panorama");

		//nombres a poner en el dropdown
		names = new List<string>();

		foreach(Texture2D tex in textures)
			names.Add(tex.name);

		foreach(VideoClip clip in clips)
			names.Add(clip.name);

		drop.AddOptions(names);

		//llamar OnChange cuando hallan cambios en dropdown
		drop.onValueChanged.AddListener(OnChange);

		//mostrar la primera textura
		loader.ShowStatic(textures[0]);
	}

	private void OnChange(int index) {
		if (index >= textures.Length) {
			loader.ShowVideo(clips[index - textures.Length]);
		} else {
			loader.ShowStatic(textures[index]);
		}
	}
}
