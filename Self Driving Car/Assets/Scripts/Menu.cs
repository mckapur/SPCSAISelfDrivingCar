using UnityEngine;
using System.Collections;
using UnityEngine.UI;

public class Menu : MonoBehaviour {

	// Use this for initialization

	/*bool shouldSendData;
	
	public void SendData() {
		shouldSendData = GameObject.Find ("Toggle").GetComponent<Toggle> ().isOn;
	}*/

	public void StartInAIMode() {
		MoveCar.isControlledByAI = true;
		if (Application.loadedLevelName == "Finished") {
			MoveCar.shouldSendData = true;
		}
		//Condition to quit game.. but don't quit before data is sent in next level
		Application.LoadLevel ("Demo");
	}

	public void StartInTrainingMode() {
		MoveCar.isControlledByAI = false;
		MoveCar.shouldSendData = false;
		Application.LoadLevel ("Demo");
	}
}

//90, 0.1, -22
//0, -90, 0