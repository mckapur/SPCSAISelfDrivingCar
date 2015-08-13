using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Text;

public class SendData : MonoBehaviour {

	//set how much gap there should be between sending data
	float getDataDelay = 0.2f;
	public static float addDataDelay = 0.2f;

	private Sensors sensor;

	void Awake() {
		//StartCoroutine (SendAndReceiveData())
		sensor = this.GetComponent<Sensors> ();
	}

	//This is only a one time thing
	public void SendDataToServer () {
		//If human is controlling, we want to send human's data for training
			//Print accumulated data
		if (sensor == null) {
			sensor = this.GetComponent<Sensors> ();
		}
		Debug.Log(sensor.SerializeList());

		string url = "http://localhost:8000/sendDrivingData";
		Dictionary<string, string> postHeaders = new Dictionary<string, string>();
		postHeaders.Add ("Content-Type", "application/json");
		byte[] bytes = Encoding.UTF8.GetBytes (sensor.SerializeList());
		WWW www = new WWW (url, bytes, postHeaders);
			// Debug.Log("We sent data correctly...");

		//StartCoroutine (WaitForRequest (www));  
	}

	//Sent by MoveCar
	public IEnumerator GetDataFromServer() {
		//If AI is controlling, then we want it to send wall input data
		while (MoveCar.isControlledByAI) {
			yield return new WaitForSeconds (getDataDelay);
			//Debug.Log("Sending distance from wall");
			string url = "http://localhost:8000/getDrivingData";
			//First send distance from wall data
			Dictionary<string, string> postHeaders = new Dictionary<string, string>();
			postHeaders.Add ("Content-Type", "application/json");
			byte[] bytes = Encoding.UTF8.GetBytes (sensor.GetDistanceToObject());
			WWW www = new WWW (url, bytes, postHeaders);
			//Receive data
			StartCoroutine(WaitForRequest(www));
		}
	}

	IEnumerator WaitForRequest(WWW www) {
		//If www is null, return
		yield return www;
		//Debug.Log ("we are receiving requests");
		if (www.error == null) {

			string receivedText = www.text;
			Debug.Log(receivedText);
			JSONObject serializedList = new JSONObject(receivedText);
			accessData(serializedList);

		}
	}

	void accessData(JSONObject obj){
		for (int i = 0; i < obj.list.Count; i++) {
			string key = (string)obj.keys[i];
			float number = obj.list[i].n;
			switch(key) {
			case "shouldAccelerate":
				//If we are moving straight and we are in front of the wall, override and break
				if(Sensors.scaledForward < 0.2f && number == 1 && MoveCar.shouldNotTurn == 1 && MoveCar.mySpeed > 30f) {
					number = 0;
				}
				MoveCar.shouldAccelerate = number;
				break;
			case "shouldTurnLeft":
				MoveCar.shouldTurnLeft = number;
				break;
			case "shouldTurnRight":
				MoveCar.shouldTurnRight = number;
				break;
			case "shouldKeepStraight":
				MoveCar.shouldNotTurn = number;
				break;
			}
		}
	}
}
