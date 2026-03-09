using UnityEngine;

[RequireComponent(typeof(MeshFilter))]
public class NormalVisualizer : MonoBehaviour {
	public bool showStoredNormals = true;
	public float lineLength = 0.2f;

	void OnDrawGizmos() {
		if(!showStoredNormals) return;
		Mesh mesh = GetComponent<MeshFilter>().sharedMesh;
		if(mesh == null) return;

		Vector3[] vertices = mesh.vertices;
		Vector3[] normals = mesh.normals;

		for(int i = 0; i < vertices.Length; i++) {
			// Convertir puntos locales a posición en el mundo
			Vector3 worldPt = transform.TransformPoint(vertices[i]);
			Vector3 worldNm = transform.TransformDirection(normals[i]);

			Gizmos.color = Color.yellow;
			Gizmos.DrawRay(worldPt, worldNm * lineLength);
		}
	}
}