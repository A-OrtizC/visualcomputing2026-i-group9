using UnityEngine;
using UnityEngine.UI; // Necesario para el Bonus del botón
using System.Collections.Generic;

public class GeneradorParametrico : MonoBehaviour
{
    // Clase simple para estructurar nuestros datos
    [System.Serializable]
    public class DatosObjeto {
        public Vector3 posicion;
        public float escala;
        public bool esEsfera;
    }

    public List<DatosObjeto> listaDatos = new List<DatosObjeto>();
    private List<GameObject> objetosCreados = new List<GameObject>();

    void Start() {
        GenerarEscena();
    }

    public void GenerarEscena() {
        // Limpiar escena previa si existe (para el botón de regenerar)
        foreach (GameObject obj in objetosCreados) {
            Destroy(obj);
        }
        objetosCreados.Clear();

        // Bucle para crear objetos desde los datos
        foreach (DatosObjeto dato in listaDatos) {
            GameObject nuevoObj;

            // Condicional: Elegir primitiva según el dato
            if (dato.esEsfera) {
                nuevoObj = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            } else {
                nuevoObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            }

            // Aplicar parámetros
            nuevoObj.transform.position = dato.posicion;
            nuevoObj.transform.localScale = Vector3.one * dato.escala;
            nuevoObj.transform.parent = this.transform; // Organizarlos bajo este script

            // Bonus: Variar color programáticamente
            Renderer rend = nuevoObj.GetComponent<Renderer>();
            rend.material.color = Color.Lerp(Color.blue, Color.red, dato.escala / 3f);

            objetosCreados.Add(nuevoObj);
        }
    }
}