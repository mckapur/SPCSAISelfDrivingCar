using UnityEngine;
using System.Collections;

public class InstantiateTaxi : MonoBehaviour {

	// Use this for initialization
	public string taxiName;

	void Awake() {
		Transform myTransform = this.GetComponent<Transform> ();

		GameObject taxi = Instantiate (Resources.Load (taxiName), myTransform.position, myTransform.rotation) as GameObject;
		taxi.name = taxiName;
	}

}
