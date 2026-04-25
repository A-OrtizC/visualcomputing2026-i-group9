using UnityEngine;
using UnityEngine.AI;

public class AIControler : MonoBehaviour
{
    private Animator animator;
    public float speed = 0;
    private Vector3 lastPos;
    public GameObject path;
    private Vector3[] nodes;
    private int nodeIndex;
	private NavMeshAgent agent;

    public float visionAngle = 60;
    public uint nrays = 10;
    private Vector3 playerPos;
	// Start is called once before the first execution of Update after the MonoBehaviour is created
	void Start()
    {
        animator = GetComponent<Animator>();
        lastPos = transform.position;
        Transform[] pathChilds = path.GetComponentsInChildren<Transform>();
        nodes = new Vector3[pathChilds.Length];
        for (int i = 0; i < pathChilds.Length; i++)
            nodes[i] = pathChilds[i].position;

		agent = GetComponent<NavMeshAgent>();
        nodeIndex = 0;
		if(nodes.Length > 0) {
            agent.SetDestination(nodes[0]);
		}
	}

	// Update is called once per frame
	void Update() {
        speed = Vector3.Distance(transform.position, lastPos) / Time.deltaTime;
		animator.SetFloat("speed", speed);
        lastPos = transform.position;

        if(searchPlayer()) {
            agent.speed = 2;
            agent.SetDestination(playerPos);
        } else {
            agent.speed = 1.5f;
            patrol();
        }
	}

    bool searchPlayer() {
        Vector3 dir = Quaternion.AngleAxis(-visionAngle / 2, Vector3.up) * transform.forward;
        Quaternion deltaRot = Quaternion.AngleAxis(visionAngle / nrays, Vector3.up);
		RaycastHit hit;
		for(uint i = 0; i < nrays; i++) {
            if (Physics.Raycast(transform.position, dir, out hit, 100f) && hit.rigidbody != null) {
                this.playerPos = hit.transform.position;
                return true;
            }
            dir = deltaRot * dir;
        }
        return false;
    }

    void patrol() {
		if(!agent.pathPending && agent.remainingDistance < 0.5f) {
			nodeIndex = (nodeIndex + 1) % nodes.Length;
			agent.SetDestination(nodes[nodeIndex]);
		}
	}
}
