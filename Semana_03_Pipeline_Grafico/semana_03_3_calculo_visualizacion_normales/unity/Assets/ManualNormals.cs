using UnityEngine;

public class ManualNormals : MonoBehaviour {
	[ContextMenu("Calcular Normales Manualmente")]
	public void Calculate() {
		Mesh mesh = GetComponent<MeshFilter>().mesh;
		Vector3[] vertices = mesh.vertices;
		int[] triangles = mesh.triangles;
		Vector3[] newNormals = new Vector3[vertices.Length];

		// Iteramos sobre los triángulos (de 3 en 3 índices)
		for(int i = 0; i < triangles.Length; i += 3) {
			int i1 = triangles[i];
			int i2 = triangles[i + 1];
			int i3 = triangles[i + 2];

			// Vectores de las aristas
			Vector3 side1 = vertices[i2] - vertices[i1];
			Vector3 side2 = vertices[i3] - vertices[i1];

			// Producto Cruz para hallar la perpendicular (Normal)
			Vector3 normal = Vector3.Cross(side1, side2).normalized;

			// Asignamos la misma normal a los 3 vértices del triángulo
			newNormals[i1] = normal;
			newNormals[i2] = normal;
			newNormals[i3] = normal;
		}

		mesh.normals = newNormals;
	}
}