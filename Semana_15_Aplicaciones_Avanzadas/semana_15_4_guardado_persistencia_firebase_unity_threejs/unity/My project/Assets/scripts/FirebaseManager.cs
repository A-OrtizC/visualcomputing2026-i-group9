// FirebaseManager.cs
// Taller 63 - Guardado y Persistencia de Datos con Firebase en Unity
//
// Este script:
//  1. Inicializa la conexión con Firebase.
//  2. Guarda la posición y rotación de un objeto 3D cada 3 segundos.
//  3. Al iniciar la escena, recupera la última posición guardada
//     y coloca el objeto exactamente ahí.
//
// INSTRUCCIONES DE USO:
//  - Crea un GameObject vacío en tu escena (ej. "FirebaseController").
//  - Arrastra este script sobre ese GameObject.
//  - En el Inspector, arrastra el objeto 3D que quieres persistir
//    (ej. un cubo, una esfera, un personaje) al campo "Target Object".

using System;
using Firebase;
using Firebase.Database;
using Firebase.Extensions;
using UnityEngine;

public class FirebaseManager : MonoBehaviour
{
    [Header("Objeto a persistir")]
    [Tooltip("Arrastra aquí el objeto 3D cuya posición/rotación quieres guardar y recuperar.")]
    public Transform targetObject;

    [Header("Configuración")]
    [Tooltip("Identificador único para este objeto dentro de la base de datos.")]
    public string objectId = "objeto_01";

    [Tooltip("Cada cuántos segundos se guarda automáticamente la posición.")]
    public float saveInterval = 3f;

    private DatabaseReference dbReference;
    private float saveTimer = 0f;
    private bool firebaseReady = false;

    void Start()
    {
        // Verifica que las dependencias de Firebase estén disponibles
        // antes de intentar usar cualquier servicio (paso obligatorio en Unity).
        FirebaseApp.CheckAndFixDependenciesAsync().ContinueWithOnMainThread(task =>
        {
            var dependencyStatus = task.Result;
            if (dependencyStatus == DependencyStatus.Available)
            {
                InitializeFirebase();
            }
            else
            {
                Debug.LogError($"[Firebase] No se pudieron resolver las dependencias: {dependencyStatus}");
            }
        });
    }

    void InitializeFirebase()
    {
        dbReference = FirebaseDatabase.DefaultInstance.RootReference;
        firebaseReady = true;
        Debug.Log("[Firebase] Inicializado correctamente.");

        // Al iniciar, recuperamos la última posición guardada
        LoadData();
    }

    void Update()
    {
        if (!firebaseReady || targetObject == null) return;

        // Acumulador de tiempo para guardar cada N segundos
        saveTimer += Time.deltaTime;
        if (saveTimer >= saveInterval)
        {
            saveTimer = 0f;
            SaveData();
        }
    }

    /// <summary>
    /// Guarda la posición y rotación actual del objeto en Firebase Realtime Database.
    /// Estructura guardada: objects/{objectId}/{position, rotation}
    /// </summary>
    void SaveData()
    {
        Vector3 pos = targetObject.position;
        Vector3 rot = targetObject.eulerAngles;

        // Construimos un diccionario con la info a guardar (similar a un JSON)
        var data = new System.Collections.Generic.Dictionary<string, object>
        {
            { "x", pos.x },
            { "y", pos.y },
            { "z", pos.z },
            { "rotX", rot.x },
            { "rotY", rot.y },
            { "rotZ", rot.z }
        };

        dbReference.Child("objects").Child(objectId).SetValueAsync(data)
            .ContinueWithOnMainThread(task =>
            {
                if (task.IsCompleted && !task.IsFaulted && !task.IsCanceled)
                {
                    Debug.Log($"[Firebase] Posición guardada: {pos} | Rotación: {rot}");
                }
                else
                {
                    Debug.LogError($"[Firebase] Error al guardar: {task.Exception}");
                }
            });
    }

    /// <summary>
    /// Recupera la última posición/rotación guardada y la aplica al objeto.
    /// Se ejecuta una sola vez al iniciar la escena.
    /// </summary>
    void LoadData()
    {
        dbReference.Child("objects").Child(objectId).GetValueAsync()
            .ContinueWithOnMainThread(task =>
            {
                if (task.IsFaulted)
                {
                    Debug.LogError($"[Firebase] Error al leer datos: {task.Exception}");
                    return;
                }

                if (task.IsCompleted)
                {
                    DataSnapshot snapshot = task.Result;

                    if (snapshot.Exists && targetObject != null)
                    {
                        float x = float.Parse(snapshot.Child("x").Value.ToString());
                        float y = float.Parse(snapshot.Child("y").Value.ToString());
                        float z = float.Parse(snapshot.Child("z").Value.ToString());
                        float rotX = float.Parse(snapshot.Child("rotX").Value.ToString());
                        float rotY = float.Parse(snapshot.Child("rotY").Value.ToString());
                        float rotZ = float.Parse(snapshot.Child("rotZ").Value.ToString());

                        targetObject.position = new Vector3(x, y, z);
                        targetObject.eulerAngles = new Vector3(rotX, rotY, rotZ);

                        Debug.Log($"[Firebase] Posición restaurada: {targetObject.position}");
                    }
                    else
                    {
                        Debug.Log("[Firebase] No hay datos previos guardados. Se usará la posición inicial del objeto.");
                    }
                }
            });
    }
}
