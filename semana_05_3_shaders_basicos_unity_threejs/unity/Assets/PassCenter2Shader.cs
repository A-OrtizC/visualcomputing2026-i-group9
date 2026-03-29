using UnityEngine;

public class PassCenter2Shader : MonoBehaviour {
	private MeshRenderer _renderer;
	public Material shaderMaterial; // Assign your Shader Graph material in the Inspector

	[ExecuteAlways]
	void Start() {
		_renderer = GetComponent<MeshRenderer>();
	}

	[ExecuteAlways]
	void Update() {
		// Calculate the world center every frame (or only when the object moves)
		Vector3 center = _renderer.bounds.center;
		// Pass it to the material's property named "_ObjectCenter"
		shaderMaterial.SetVector("_ObjectCenter", center);
	}
}
