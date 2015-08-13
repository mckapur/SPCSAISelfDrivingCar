using UnityEngine;
using System.Collections;
using UnityEngine.UI;

public class Menu : MonoBehaviour {

	public static string chooseScene = "Demo";

	public void ChooseBrakes() {
		chooseScene = "BrakingScene2";
	}

	public void StartInAIMode() {
		MoveCar.isControlledByAI = true;
		if (Application.loadedLevelName == "Finished") {
			MoveCar.shouldSendData = true;
		}
		//Condition to quit game.. but don't quit before data is sent in next level
		Application.LoadLevel (chooseScene);
	}

	public void StartInTrainingMode() {
		MoveCar.isControlledByAI = false;
		MoveCar.shouldSendData = false;
		int chance = Random.Range (1, 3); //1 to 2
		switch (chance) { 
		case 1:
			chooseScene = "Demo";
			break;
		case 2:
			chooseScene = "Demo2";
			break;
		default:
			Debug.Log("lol you suck at programming");
			break;
		}
		Application.LoadLevel (chooseScene);
	}
}

//90, 0.1, -22
//0, -90, 0