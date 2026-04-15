using UnityEngine;

public class Player : MonoBehaviour
{
    public float walkSpeed = 2f;
    public float runSpeed = 5f;
    public float rotationSpeed = 10f;

    public bool useUIControl = false; // 🔥 controla si UI manda

    private Animator animator;
    private bool isPerformingAction = false;

    void Start()
    {
        animator = GetComponent<Animator>();
        animator.applyRootMotion = false; // 🚫 evitar movimiento por animación
    }

    void Update()
    {
        if (isPerformingAction)
        {
            CheckIfActionFinished();
            return; // 🚫 no se puede mover
        }
        // 🎮 Si UI está controlando, NO hacer lógica de movimiento
        if (useUIControl)
        {
            return;
        }

        float h = 0f;
        float v = 0f;

        if (Input.GetKey(KeyCode.A)) h = -1f;
        if (Input.GetKey(KeyCode.D)) h = 1f;
        if (Input.GetKey(KeyCode.W)) v = 1f;
        if (Input.GetKey(KeyCode.S)) v = -1f;

        Vector3 direction = new Vector3(h, 0, v);
        bool isMoving = direction.magnitude > 0.1f;

        if (isMoving)
        {
            direction.Normalize();

            bool isRunning = Input.GetKey(KeyCode.LeftShift);
            float speed = isRunning ? runSpeed : walkSpeed;

            animator.SetFloat("Speed", isRunning ? 1f : 0.4f);

            Quaternion targetRotation = Quaternion.LookRotation(direction);
            transform.rotation = Quaternion.Slerp(
                transform.rotation,
                targetRotation,
                rotationSpeed * Time.deltaTime
            );

            transform.position += direction * speed * Time.deltaTime;
        }
        else
        {
            if (Input.GetKeyDown(KeyCode.Space) && !isPerformingAction)
            {
                animator.SetTrigger("Wave");
                isPerformingAction = true;
            }

            animator.SetFloat("Speed", 0f);
        }
    }


    // 🎯 Permite que UI reproduzca animación
    public void PlayAnimation(string animName)
    {
        useUIControl = true;

        animator.ResetTrigger("Wave");
        animator.Play(animName, 0, 0f);
    }

    // 🔄 Reiniciar animación actual
    public void RestartAnimation()
    {
        AnimatorStateInfo state = animator.GetCurrentAnimatorStateInfo(0);
        animator.Play(state.fullPathHash, 0, 0f);
    }

    // ▶️ Volver a control normal
    public void ResumePlayer()
    {
        useUIControl = false;
    }

    // ⏸️ Pausar animación
    public void PauseAnimation()
    {
        animator.speed = 0f;
    }

    // ▶️ Reanudar animación
    public void ResumeAnimation()
    {
        animator.speed = 1f;
    }

    void CheckIfActionFinished()
    {
        AnimatorStateInfo state = animator.GetCurrentAnimatorStateInfo(0);

        // 🔥 si ya terminó la animación
        if (state.IsName("waving") && state.normalizedTime >= 1f)
        {
            isPerformingAction = false;
        }
    }
}