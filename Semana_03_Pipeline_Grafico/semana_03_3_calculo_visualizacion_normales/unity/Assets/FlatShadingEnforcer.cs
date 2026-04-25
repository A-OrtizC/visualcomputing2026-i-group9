using UnityEngine;

public class FlatShadingEnforcer : MonoBehaviour {
	[ContextMenu("Convertir a Flat Shading (Corregido)")]
	public void MakeFlat() {
		MeshFilter mf = GetComponent<MeshFilter>();
		if(mf == null || mf.sharedMesh == null) return;

		Mesh oldMesh = mf.sharedMesh;

		// 1. Obtener los datos actuales
		Vector3[] oldVertices = oldMesh.vertices;
		int[] oldTriangles = oldMesh.triangles;

		// 2. Crear nuevos arreglos: Cada índice de triángulo será un nuevo vértice
		Vector3[] newVertices = new Vector3[oldTriangles.Length];
		int[] newTriangles = new int[oldTriangles.Length];

		for(int i = 0; i < oldTriangles.Length; i++) {
			// Copiamos el vértice original a una nueva posición en el array
			newVertices[i] = oldVertices[oldTriangles[i]];
			// El nuevo índice es simplemente la posición secuencial
			newTriangles[i] = i;
		}

		// 3. Crear la nueva malla facetada
		Mesh newMesh = new Mesh();
		newMesh.name = oldMesh.name + "_Flat";
		newMesh.vertices = newVertices;
		newMesh.triangles = newTriangles;

		// 4. Calcular normales (al no haber vértices compartidos, serán perpendiculares a cada cara)
		newMesh.RecalculateNormals();

		// 5. Opcional: Recalcular Tangentes para que los materiales con Normal Map funcionen
		newMesh.RecalculateTangents();

		// Asignar la nueva malla al MeshFilter
		mf.mesh = newMesh;

	}
}