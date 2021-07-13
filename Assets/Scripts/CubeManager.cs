using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CubeManager : MonoBehaviour
{
    public static CubeManager instance = null;

    [SerializeField]
    private GameObject cubePrefab;

    [SerializeField]
    [Range(1,3000)]
    private int cubeNumber;

    public List<Cube> cubes = new List<Cube>();

    [Range(-100,100)]
    public float maxX, maxY, minX, minY;

    [SerializeField]
    private bool sap = true;

    void Awake()
    {
        if(instance == null)
        {
            Random.InitState(2333);
            instance = this;
        }    
    }
    void Start()
    {
        for(int i = 0;i < cubeNumber; i++)
        {
            GameObject cube = Instantiate(cubePrefab, getRandomPosition(), Quaternion.identity);
            cube.transform.parent = transform;
            Cube c = cube.GetComponent<Cube>();
            cubes.Add(c);
            c.id = cubes.Count - 1;
            c.direction = new Vector3(Random.Range(-1f, 1f), 0f,Random.Range(-1f, 1f)).normalized;
            c.speed = Random.Range(2f, 4f);
        }
        
    }

    private Vector3 getRandomPosition()
    {
        return new Vector3(Random.Range(minX,maxX), 0.5f, Random.Range(minY, maxY));
    }
    // Update is called once per frame
    void Update()
    {
        
    }

}
