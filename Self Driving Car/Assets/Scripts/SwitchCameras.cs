using UnityEngine;
using System.Collections;

public class SwitchCameras : MonoBehaviour {

	public Camera thirdPersonCam;
	public Camera firstPersonCam;
	bool usingThirdPerson;

	void Start() {
		usingThirdPerson = true;
	}

	void Update () {
		if(Input.GetKeyDown("r")) {
			usingThirdPerson = !usingThirdPerson;
			if (usingThirdPerson) {
				thirdPersonCam.enabled = true;
				firstPersonCam.enabled = false;
			} else {
				firstPersonCam.enabled = true;
				thirdPersonCam.enabled = false;
			}
		}
	}
}
