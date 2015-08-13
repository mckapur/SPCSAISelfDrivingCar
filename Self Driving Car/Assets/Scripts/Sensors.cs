using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class Sensors : MonoBehaviour {
	//private float leftwardColliderDistance, forwardColliderDistance, rightwardColliderDistance;
	public static float scaledForward;
	private float maxScaledLeft, maxScaledRight, scaledLRRatio;

	public Transform leftwardSensorLocation, forwardSensorLocation, rightwardSensorLocation;
	//Visualization of where we hit.
	public GameObject leftwardRayHitPoint, forwardRayHitPoint, rightwardRayHitPoint;

	public Camera cam;
	
	public float rayIncrementAngle = 15f;
	public float rayMaxAngle = 75f;
	public float rayStartAngle = 10f;

	//store multiple variables in one list
	public static List<Values> informationList;
	
	private static JSONObject _serializedObject;
	MoveCar moveCar;

	private void Awake() {
		moveCar = this.GetComponent<MoveCar> ();
		leftwardRayHitPoint = GameObject.Find ("LeftRay");
		forwardRayHitPoint = GameObject.Find ("CenterRay");
		rightwardRayHitPoint = GameObject.Find ("RightRay");

		//So that this does not reset every turn
		if (informationList == null) {
			informationList = new List<Values> ();
		}
	}

	//Recording human data for training
	public string SerializeList () {
		_serializedObject = new JSONObject (JSONObject.Type.OBJECT);
		JSONObject data = new JSONObject(JSONObject.Type.ARRAY);
		foreach (Values v in informationList) {
			JSONObject trainingCase = new JSONObject(JSONObject.Type.OBJECT);
			//trainingCase.AddField("normalizedSpeed", MoveCar.normalizedSpeed);
			trainingCase.AddField("scaledForward", v.sentScaledForward);
			trainingCase.AddField("scaledLeftRightRatio", v.sentScaledLRRatio);
			trainingCase.AddField("isAccelerating", v.isAccelerating);
			trainingCase.AddField("scaledSpeed", v.sentScaledSpeed);

			trainingCase.AddField("isTurningLeft", v.isTurningLeft);
			trainingCase.AddField("isTurningRight", v.isTurningRight);
			trainingCase.AddField("isKeepingStraight", v.isNotTurning);
			data.Add(trainingCase);
		}
		_serializedObject.AddField("data", data);
		JSONObject types = new JSONObject(JSONObject.Type.ARRAY);
		types.Add ("motion");
		types.Add ("steering");
		_serializedObject.AddField("types", types);
		return _serializedObject.Print ();
	}

	//Server sending server data to 3d environment
	public string GetDistanceToObject () {
		_serializedObject = new JSONObject (JSONObject.Type.OBJECT);
		JSONObject trainingCase = new JSONObject(JSONObject.Type.OBJECT);
		trainingCase.AddField("scaledSpeed", MoveCar.scaledSpeed);
		trainingCase.AddField("scaledForward", scaledForward);
		trainingCase.AddField("scaledLeftRightRatio", scaledLRRatio);
		_serializedObject.AddField("data", trainingCase);
		JSONObject types = new JSONObject(JSONObject.Type.ARRAY);
		types.Add ("motion");
		types.Add ("steering");
		_serializedObject.AddField("types", types);
		return _serializedObject.Print ();
	}

	public void ClearList() {
		Debug.Log("Cleared list");
		if (informationList != null) {
			informationList.Clear ();
		}
	}

	void Update () {
		//Only send leftray
		maxScaledRight = FindWidestRightRay (rayStartAngle, rayMaxAngle, rayIncrementAngle);
		maxScaledLeft = FindWidestLeftRay (-rayMaxAngle, -rayStartAngle, rayIncrementAngle);

		//This is a formula to come up with a ratio from those two
		//0 is left, 0.5 is straight, 1.0 is right
		scaledLRRatio = Mathf.Clamp01 ((maxScaledLeft + maxScaledRight + 1f) / 2f);
	
		//This should figure out the general direction..
		if (scaledLRRatio >= 0.5f) {
			scaledForward = FindLongestForwardRay (0f, 10f, 5f);
		} else {
			scaledForward = FindLongestForwardRay (-10f, 0f, 5f);
		}
	}


	float FindWidestRightRay(float minAngle, float maxAngle, float angleIncrement) {
		float maxScaled = 0f;
		Vector2 finalPositionOnScreen = Vector2.zero;
		//15, 30, 45, 60, 75
		for(float angle = minAngle; angle <= maxAngle; angle += angleIncrement) {
			Vector2 positionOnScreen = SendRay(angle);
			float scaled = (positionOnScreen.x - Screen.width/2)/(Screen.width/2);
			scaled = Mathf.Clamp(scaled, 0f, 1f);
			//save max
			if(scaled > maxScaled) {
				maxScaled = scaled;
				finalPositionOnScreen = positionOnScreen;
			}
		}
		rightwardRayHitPoint.transform.position = finalPositionOnScreen;
		return maxScaled;
	}

	float FindWidestLeftRay(float minAngle, float maxAngle, float angleIncrement) {
		float minScaled = 1f;
		Vector2 finalPositionOnScreen = Vector2.zero;
		//15, 30, 45, 60, 75
		for(float angle = minAngle; angle <= maxAngle; angle += angleIncrement) {
			Vector2 positionOnScreen = SendRay(angle);
			float scaled = (positionOnScreen.x - Screen.width/2)/(Screen.width/2);
			scaled = Mathf.Clamp(scaled, -1f, 0f);
			//save max
			if(scaled < minScaled) {
				minScaled = scaled;
				finalPositionOnScreen = positionOnScreen;
			}
		}
		leftwardRayHitPoint.transform.position = finalPositionOnScreen;
		return minScaled;
	}
	
	//11 in total
	//15, 30, 45, 60, 75
	//0
	//-15, -30, -45, -60, -75
	Vector2 SendRay (float angle) {
		RaycastHit hit;
		Quaternion rotation = Quaternion.identity;
		rotation.eulerAngles = new Vector3 (0f, angle, /*Mathf.Abs(angle)*/0f);
		Vector3 direction = rotation * transform.forward;
		Vector3 sensorPosition = forwardSensorLocation.position;
		Ray ray = new Ray(sensorPosition, direction);

		//limit max distance..
		//send raycasts at different distances
		if (Physics.Raycast(ray, out hit)) {
			Vector2 positionOnScreen = cam.WorldToScreenPoint(hit.point);
			Debug.DrawLine(sensorPosition, hit.point, Color.red);
			return positionOnScreen;
		}	
		return Vector2.zero;
	}

	float FindLongestForwardRay(float minAngle, float maxAngle, float angleIncrement) {
		float maxDistance = 0f;
		Vector3 furthestHitPoint = Vector3.zero;
		//15, 30, 45, 60, 75
		for(float angle = minAngle; angle <= maxAngle; angle += angleIncrement) {
			RaycastHit hit;
			Vector3 direction = Quaternion.AngleAxis (angle, Vector3.up)* transform.forward;
			Ray forwardRay = new Ray(forwardSensorLocation.position, direction);

			if (Physics.Raycast(forwardRay, out hit)) {
				float distance = hit.distance;
				//save max
				if(distance > maxDistance) {
					maxDistance = distance;
					furthestHitPoint = hit.point;
				}
				Debug.DrawLine(forwardSensorLocation.position, hit.point, Color.red);
			}
		}
		forwardRayHitPoint.transform.position = cam.WorldToScreenPoint(furthestHitPoint);
		return moveCar.Map(0f, 50f, 0f, 1f, maxDistance);
	}

	public IEnumerator addInformationList() {
		while (!MoveCar.isControlledByAI) {
			yield return new WaitForSeconds (SendData.addDataDelay);
			//Send data only when the person starts accelerating
			informationList.Add (new Values {
				sentScaledSpeed = MoveCar.scaledSpeed,
				sentScaledForward = scaledForward,
				sentScaledLRRatio = scaledLRRatio,
				isAccelerating = MoveCar.isAccelerating,
				isTurningLeft = MoveCar.isTurningLeft,
				isTurningRight = MoveCar.isTurningRight,
				isNotTurning = MoveCar.isNotTurning
			});
		}
	}

	void OnCollisionStay(Collision other) {
		if (other.gameObject.tag == "Finish" && !MoveCar.isFinished && MoveCar.mySpeed < 1f) {
			moveCar.IsFinished(false);
		}
	}

	void OnCollisionEnter(Collision other) {
		if (other.gameObject.tag == "Wall" && !MoveCar.isFinished && !MoveCar.isControlledByAI) {
			moveCar.IsFinished(true);
		}
	}
	
	//This prints data to the game view itself...
	void OnGUI() {
		//Left ray
		GUI.Button (new Rect (10, 20, 200, 30), "ScaledLR: " + scaledLRRatio);
		GUI.Button (new Rect (Screen.width/2-100, 50, 200, 30), "Forward ratio: " + scaledForward);
		
		GUI.Button (new Rect (10, 80, 150, 30), "Speed: " + Mathf.Round(MoveCar.mySpeed) + " km/h");
		GUI.Button (new Rect (10, 50, 200, 30), "AI is Driving: " + MoveCar.isControlledByAI);

		if (GUI.Button (new Rect (Screen.width - 180, 20, 160, 30), "Quit")) {
			Debug.Log("Quit");
			Application.LoadLevel("Start");
			//moveCar.LoadLevel("Start",0f);
		}
	}

	void OnApplicationQuit() {
		ClearList ();
	}

	public struct Values {
		//public float normalizedSpeed;
		public float sentScaledSpeed;
		public float sentScaledForward;
		public float sentScaledLRRatio;
		public float isAccelerating;
		public float isTurningLeft;
		public float isTurningRight;
		public float isNotTurning;
	}
}                                                                   