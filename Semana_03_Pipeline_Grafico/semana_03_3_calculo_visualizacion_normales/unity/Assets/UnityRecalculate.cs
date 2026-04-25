using UnityEngine;

public class UnityRecalculate : MonoBehaviour {
	[ContextMenu("Usar RecalculateNormals()")]
	public void QuickRecalculate() {
		Mesh mesh = GetComponent<MeshFilter>().mesh;

		// Unity promedia automáticamente las normales de vértices compartidos
		mesh.RecalculateNormals();
	}
}