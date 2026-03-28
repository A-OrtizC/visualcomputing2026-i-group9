using UnityEngine;
using UnityEditor;

[CustomEditor(typeof(ObjectGen))] // Tells Unity this is an editor for MyScript
public class MyScriptEditor : Editor {
	public override void OnInspectorGUI() {
		//DrawDefaultInspector();
		ObjectGen script = (ObjectGen)target;

		script.numObj = (uint) EditorGUILayout.IntField("Number of objects", (int) script.numObj);
		script.objType = (PrimitiveType)EditorGUILayout.EnumPopup("Primitive type", script.objType);

		EditorGUILayout.LabelField("", GUI.skin.horizontalSlider);
		EditorGUILayout.LabelField("Individual object transform");
		script.rotation = EditorGUILayout.Vector3Field("Rotation", script.rotation);
		script.scale = EditorGUILayout.Vector3Field("Scale", script.scale);

		EditorGUILayout.LabelField("", GUI.skin.horizontalSlider);
		EditorGUILayout.LabelField("Structure of objects");
		script.structure = (ObjectGen.Structure) EditorGUILayout.EnumPopup("Structure", script.structure);

		switch (script.structure) {
			case (ObjectGen.Structure.grid):
				script.gridSize = EditorGUILayout.Vector2Field("Grid size", script.gridSize);
				break;
			case (ObjectGen.Structure.spiral):
				script.spiralAngleOff = EditorGUILayout.FloatField("Angle change", script.spiralAngleOff);
				script.spiralHeight = EditorGUILayout.FloatField("Height", script.spiralHeight);
				script.spiralRadius = EditorGUILayout.FloatField("Radius", script.spiralRadius);
				break;
			case (ObjectGen.Structure.pyramid):
				script.pyramidHeight = EditorGUILayout.FloatField("Height", script.pyramidHeight);
				break;
		}

		//GUILayout.Space(10);
		// Add a space before the button
		EditorGUILayout.LabelField("", GUI.skin.horizontalSlider);
		GUILayout.Space(10);

		if(GUILayout.Button("Destroy objects"))
			script.destroyChildObj();
		if(GUILayout.Button("Create objects"))
			script.createObjects();
		if (script.structure == ObjectGen.Structure.pyramid) {
			script.pyramidDepth = (uint)EditorGUILayout.IntField("Pyramid recursive depth", (int)script.pyramidDepth);
			if(GUILayout.Button("Generate mesh"))
				script.genPyramidMesh();
		}
	}
}