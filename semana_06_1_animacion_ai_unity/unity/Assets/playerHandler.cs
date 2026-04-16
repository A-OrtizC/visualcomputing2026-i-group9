using UnityEngine;

public class playerHandler : MonoBehaviour
{
    public float speed = 2;
	public float sensitivity = 2.0f;
	float rotationX = 0;
	float rotationY = 0;
	Rigidbody rb;
	// Start is called once before the first execution of Update after the MonoBehaviour is created
	void Start() {
		rb = GetComponent<Rigidbody>();
    }

    // Update is called once per frame
    void Update() {
		Vector3 dir1 = transform.forward;
		dir1.y = 0;
		dir1.Normalize();
		Vector3 dir2 = transform.right;
		dir2.y = 0;
		dir2.Normalize();
		rb.linearVelocity = speed * (
            dir1 * Input.GetAxis("Vertical") +
			dir2 * Input.GetAxis("Horizontal")
            );

		rotationY += Input.GetAxis("Mouse X") * sensitivity;
		rotationX -= Input.GetAxis("Mouse Y") * sensitivity;

		// Clamp vertical rotation to prevent flipping the camera upside down
		rotationX = Mathf.Clamp(rotationX, -90f, 90f);

		// Apply rotation
		transform.localRotation = Quaternion.Euler(rotationX, rotationY, 0);
	}
}
