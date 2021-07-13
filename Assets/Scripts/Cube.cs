using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Cube : MonoBehaviour
{
    // Start is called before the first frame update
    private Material material;
    public int id;
    private Rigidbody rb;
    public Vector3 direction = Vector3.forward;
    public float speed = 1.2f;
    void Start()
    {
        rb = GetComponent<Rigidbody>();
        material = GetComponent<MeshRenderer>().material;
    }

    // Update is called once per frame
    void Update()
    {
        rb.MovePosition(transform.position + direction * speed * Time.deltaTime);
        //transform.Translate(direction * speed * Time.deltaTime);
        Vector2 pos = new Vector2(transform.position.x, transform.position.z);
        if(pos.x >= CubeManager.instance.maxX || pos.x <= CubeManager.instance.minX)
        {
            direction.x *= -1;
        }
        if(pos.y >= CubeManager.instance.maxY || pos.y <= CubeManager.instance.minY)
        {
            direction.z *= -1;
        }
    }
    void OnTriggerStay(Collider other)
    {
        if(other.CompareTag("Player"))
        {
            material.color = new Color(255, 0, 0);
        }
    }
    void OnTriggerExit(Collider other)
    {
        if(other.CompareTag("Player"))
        {
            material.color = new Color(0, 255, 0);
        }    
    }
}
