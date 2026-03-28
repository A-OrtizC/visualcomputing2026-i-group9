using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using Unity.Mathematics;
using UnityEngine;


public class ObjectGen : MonoBehaviour
{
    public enum Structure {
        grid,
        spiral,
        pyramid
    };

    //objects data
    private GameObject []objects;
    public PrimitiveType objType;
    public uint numObj;
    public Vector3 rotation;
    public Vector3 scale;

    //structure data
    public Structure structure;
    public Vector2 gridSize;
    public float spiralRadius;
    public float spiralAngleOff;
	public float spiralHeight;
    public float pyramidHeight;

    //for mesh creation
    public uint pyramidDepth;
    private Vector3 []meshVert;
    private int[] meshTri;
    private int vertUsed;
    private uint triUsed;

	public void destroyChildObj() {
        if(objects != null) {
            foreach(GameObject obj in objects) {
                DestroyImmediate(obj);
            }
        }
        objects = null;
    }

    private IEnumerable<Vector3> gridPositions() {
        int objPerSide = (int)math.ceil(math.sqrt(this.numObj));
        float xMul = this.gridSize.x / objPerSide;
        float yMul = this.gridSize.y / objPerSide;
        for(int i = 0; i < this.numObj; i++) {
            int x = i % objPerSide;
            int y = (int)(i / objPerSide);
            yield return new Vector3(x * xMul, y * yMul);
        }
    }
	private IEnumerable<Vector3> spiralPositions() {
		for(int i = 0; i < this.numObj; i++) {
			float t = (float) i / (float) (this.numObj - 1);
            float angle = i * this.spiralAngleOff;
			yield return new Vector3(
                this.spiralRadius * math.cos(angle),
				this.spiralHeight * t,
				this.spiralRadius * math.sin(angle)
				);
		}
	}

    private IEnumerable<Vector3> recursivePyramid(Vector3 A, Vector3 B, Vector3 C, Vector3 D) {
        //returns in the form 2 * (4^n - 1) where n is the depth of recursive calls
        Vector3 AB = (A + B) / 2;
		yield return AB;
        Vector3 AC = (A + C) / 2;
		yield return AC;
        Vector3 AD = (A + D) / 2;
        yield return AD;
        Vector3 BC = (B + C) / 2;
        yield return BC;
        Vector3 BD = (B + D) / 2;
        yield return BD;
		Vector3 CD = (C + D) / 2;
		yield return CD;

		var sub1 = recursivePyramid(A, AB, AC, AD);
        var sub2 = recursivePyramid(AB, B, BC, BD);
        var sub3 = recursivePyramid(AC, BC, C, CD);
        var sub4 = recursivePyramid(AD, BD, CD, D);

        uint maxRet = 6;
        var subs = new IEnumerator<Vector3>[] {
            sub1.GetEnumerator(),
			sub2.GetEnumerator(),
			sub3.GetEnumerator(),
			sub4.GetEnumerator()
		};
        while(true) {
            foreach(var sub in subs) {
                for(uint i = 0; i < maxRet; i++) {
                    sub.MoveNext();
                    yield return sub.Current;
                }
            }
            maxRet <<= 2;
        }
	}

	private IEnumerable<Vector3> pyramidPositions() {
        Vector3 A, B, C, D;
        A = Vector3.up * this.pyramidHeight;
        float fromCenter = this.pyramidHeight / math.sqrt(3);
        B = new Vector3(math.cos(math.PI * 2 / 3) * fromCenter, 0, math.sin(math.PI * 2 / 3) * fromCenter);
        C = new Vector3(math.cos(math.PI * 4 / 3) * fromCenter, 0, math.sin(math.PI * 4 / 3) * fromCenter);
        D = new Vector3(math.cos(math.PI * 2) * fromCenter, 0, math.sin(math.PI * 2) * fromCenter);
        var vecEnum = recursivePyramid(A, B, C, D).GetEnumerator();
        if (this.numObj > 0)
            yield return A;
        if (this.numObj > 1)
            yield return B;
        if (this.numObj > 2)
		    yield return C;
        if (this.numObj > 3)
            yield return D;
		for(uint i = 0; i < this.numObj - 4 && vecEnum.MoveNext(); i++) {
            yield return vecEnum.Current;
        }
	}

	public void createObjects() {
        destroyChildObj();
        this.objects = new GameObject[this.numObj];

        //position iterable
        Func<IEnumerable<Vector3>> iterable = null;
        switch (this.structure) {
            case Structure.grid:
                iterable = gridPositions;
                break;
			case Structure.spiral:
                iterable = spiralPositions;
				break;
			case Structure.pyramid:
                iterable = pyramidPositions;
                break;
		}

        uint i = 0;
        foreach (Vector3 pos in iterable()) {
		    GameObject obj = GameObject.CreatePrimitive(this.objType); //create obj

            //initialize obj
            obj.transform.parent = gameObject.transform;
            obj.transform.localPosition = pos;
            obj.transform.rotation = Quaternion.Euler(this.rotation);
            obj.transform.localScale = this.scale;

            this.objects[i++] = obj; //add to obj array
        }

    }

    public void genPyramidMesh() {
        uint numVert = 0;
        uint numTri = 1;
		if (pyramidDepth > 0) {
            numTri = (uint)4 << ((int) this.pyramidDepth - 1) * 2;
            numVert = (numTri - 1) << 1;
        }
        numTri *= 12;
		numVert += 4;
		this.meshVert = new Vector3[numVert];
        this.meshTri = new int[numTri];
        triUsed = 0;

		meshVert[0] = Vector3.up * this.pyramidHeight;
		float fromCenter = this.pyramidHeight / math.sqrt(3);
		meshVert[1] = new Vector3(math.cos(math.PI * 2 / 3) * fromCenter, 0, math.sin(math.PI * 2 / 3) * fromCenter);
		meshVert[2] = new Vector3(math.cos(math.PI * 4 / 3) * fromCenter, 0, math.sin(math.PI * 4 / 3) * fromCenter);
		meshVert[3] = new Vector3(math.cos(math.PI * 2) * fromCenter, 0, math.sin(math.PI * 2) * fromCenter);
        vertUsed = 4;

        genPyramidMesh(0, 1, 2, 3, 0);

        Mesh pyramid = new Mesh();
        pyramid.vertices = meshVert;
        pyramid.triangles = meshTri;
        pyramid.RecalculateNormals();

        gameObject.GetComponent<MeshFilter>().mesh = pyramid;
	}
    public void genPyramidMesh(int a, int b, int c, int d, int depth) {
        if (depth < this.pyramidDepth) {
            meshVert[vertUsed] = (meshVert[a] + meshVert[b]) / 2;
            int ab = vertUsed++;
			meshVert[vertUsed] = (meshVert[a] + meshVert[c]) / 2;
			int ac = vertUsed++;
			meshVert[vertUsed] = (meshVert[a] + meshVert[d]) / 2;
			int ad = vertUsed++;
			meshVert[vertUsed] = (meshVert[b] + meshVert[c]) / 2;
			int bc = vertUsed++;
			meshVert[vertUsed] = (meshVert[b] + meshVert[d]) / 2;
			int bd = vertUsed++;
			meshVert[vertUsed] = (meshVert[c] + meshVert[d]) / 2;
			int cd = vertUsed++;

			genPyramidMesh(a, ab, ac, ad, ++depth);
			genPyramidMesh(ab, b, bc, bd, depth);
			genPyramidMesh(ac, bc, c, cd, depth);
			genPyramidMesh(ad, bd, cd, d, depth);
            return;
        }
        meshTri[triUsed++] = b;
        meshTri[triUsed++] = a;
        meshTri[triUsed++] = c;

		meshTri[triUsed++] = c;
		meshTri[triUsed++] = a;
		meshTri[triUsed++] = d;

		meshTri[triUsed++] = d;
		meshTri[triUsed++] = a;
		meshTri[triUsed++] = b;

		meshTri[triUsed++] = b;
		meshTri[triUsed++] = c;
		meshTri[triUsed++] = d;
	}
}
