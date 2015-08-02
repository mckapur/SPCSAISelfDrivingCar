using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class Sensors : MonoBehaviour {
	//private float leftwardColliderDistance, forwardColliderDistance, rightwardColliderDistance;
	private float scaledForward, maxScaledLeft, maxScaledRight, scaledLRRatio;

	public Transform leftwardSensorLocation, forwardSensorLocation, rightwardSensorLocation;
	//Visualization of where we hit.
	public GameObject leftwardRayHitPoint, forwardRayHitPoint, rightwardRayHitPoint;

	public Camera cam;
	
	public float rayIncrementAngle = 15f;
	public float rayMaxAngle = 75f;

	//store multiple variables in one list
	public static List<Values> informationList;

	void Start() {
		//Dictionary<float, Values> information = new Dictionary<float, Values>();

		//So that this does not reset every turn
		if (informationList == null) {
			Debug.Log("Cleared list from awake");
			informationList = new List<Values> ();
		}
	}

	private static JSONObject _serializedObject;
	MoveCar moveCar;

	private void Awake() {
		moveCar = this.GetComponent<MoveCar> ();
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
		if (informationList != null) {
			informationList.Clear ();
		}
	}

	void Update () {
		//Only send leftray
			maxScaledRight = FindLongestRightRay (rayIncrementAngle, rayMaxAngle);
			maxScaledLeft = FindLongestLeftRay (rayIncrementAngle, rayMaxAngle);

			//This is a formula to come up with a ratio from those two
			//0 is left, 0.5 is straight, 1.0 is right
			scaledLRRatio = Mathf.Clamp01 ((maxScaledLeft + maxScaledRight + 1f) / 2f);

			//This is neccessary because it returns a different scaled value
			scaledForward = ForwardRay ();
	}


	float FindLongestRightRay(float angleIncrement, float maxAngle) {
		float maxScaled = 0f;
		Vector2 finalPositionOnScreen = Vector2.zero;
		//15, 30, 45, 60, 75
		for(float angle = angleIncrement; angle <= maxAngle; angle += angleIncrement) {
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

	float FindLongestLeftRay(float angleIncrement, float maxAngle) {
		float minScaled = 1f;
		Vector2 finalPositionOnScreen = Vector2.zero;
		//15, 30, 45, 60, 75
		for(float angle = angleIncrement; Mathf.Abs(angle) <= Mathf.Abs(maxAngle); angle -= angleIncrement) {
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
		Vector3 direction = Quaternion.AngleAxis (angle, Vector3.up) * transform.forward;
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
	
	float ForwardRay() {
		RaycastHit hit;
		//Send ray forward from the center
		Vector3 direction = Quaternion.AngleAxis (0f, Vector3.up) * transform.forward;
		Ray forwardRay = new Ray(forwardSensorLocation.position, direction);
		if (Physics.Raycast(forwardRay, out hit)) {
			float forwardColliderDistance = Mathf.Round(hit.distance);
			forwardRayHitPoint.transform.position = cam.WorldToScreenPoint(hit.point);
			return moveCar.Map(0f, 50f, 0f, 1f, forwardColliderDistance);
		}
		Debug.LogError ("This should never happen");
		return 0;
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
		/*GUI.Button (new Rect (210, 20, 200, 30), "ScaledLeft: " + scaledLeft);
		GUI.Button (new Rect (410, 20, 200, 30), "ScaledRIght: " + scaledRight);*/
		//Forward ray
		GUI.Button (new Rect (Screen.width/2-100, 50, 200, 30), "Forward ratio: " + scaledForward);
		//Right ray
		
		GUI.Button (new Rect (10, 80, 150, 30), "Speed: " + Mathf.Round(MoveCar.mySpeed) + " km/h");
		GUI.Button (new Rect (10, 50, 200, 30), "AI is Driving: " + MoveCar.isControlledByAI);
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