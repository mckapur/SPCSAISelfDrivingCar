using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;

public class MoveCar : MonoBehaviour {

	/*Car physics vairables*/

	public List<AxleInfo> axleInfos; // the information about each individual axle
	public float maxMotorTorque; // maximum torque the motor can apply to wheel
	public float maxBrakeTorque;
	public float maxSteeringAngle; // maximum steer angle the wheel can have

	private Rigidbody rb;
	public float maxSpeed = 100f; //*3.6
	//speed = velocity.magnitude
	public static float mySpeed;
	public static float scaledSpeed;

	private Vector3 initialPosition;
	private Quaternion initialRotation;
	//Default COM is 0, 0.3, 0
	private Vector3 centerOfMass = new Vector3(0, 0, 0);

	/*Sound variables*/
	public AudioClip movingCarSound;
	private AudioSource audioSource; 

	/*Car move varibles*/
	//This is data that will be sent to the python learning script If one is 1 then the rest are 0
	public static float isAccelerating;
	//Python neural network will control these variables. If one is 1, then the rest are 0
	public static float shouldAccelerate = 0;

	/*Car turning variables*/
	//Data sent to server
	public static float isTurningLeft;
	public static float isTurningRight;
	public static float isNotTurning;
	//Data received from server
	public static float shouldTurnLeft = 0;
	public static float shouldTurnRight = 0;
	public static float shouldNotTurn = 0;

	/*Game state variables*/
	public static bool isFinished;
	//True means AI is driving
	//False means human is training AI
	public static bool isControlledByAI;

	/*GUI variables*/
	//public Text crashText;
	public Text finishText;

	private SendData sendData;
	private Sensors sensors;
	//private SensorsNoWall sensors2;

	private bool begunAccelerating;
	public static bool shouldSendData;
	
	private bool crashed;

	public void Awake() {

		//TODO: Make a loading scene to wait for data after we send data...

		finishText = GameObject.Find ("Finished").GetComponent<Text> ();
		//crashText.text = "";

		sendData = this.GetComponent<SendData>();

		sensors = this.GetComponent<Sensors> ();
		
		initialPosition = transform.position;
		initialRotation = transform.rotation;

		rb = GetComponent<Rigidbody> ();
		rb.centerOfMass = centerOfMass;
		audioSource = GetComponent<AudioSource> ();
		if (MoveCar.isControlledByAI) {
			//Change to IEnumerator
			StartCoroutine(sendData.GetDataFromServer());
		}
		StartAgain ();
		//Start sending data only when acceleration is pressed for the first time
	}

	void StartAgain() {
		isFinished = false;

		audioSource.volume = 0f;

		Debug.Log ("Started again");
		//Reset car position
		transform.position = initialPosition;
		transform.rotation = initialRotation;

		finishText.text = "";
		begunAccelerating = false;

		isAccelerating = 0;
		if (crashed) {
			Debug.Log("We had crashed");
			sensors.ClearList();
		}
		if (shouldSendData) {
			Debug.Log ("Sending data..");
			sendData.SendDataToServer ();
			sensors.ClearList ();
			shouldSendData = false;
			Debug.Log("Quit");
			Application.LoadLevel("Start");
		}
		else if (MoveCar.isControlledByAI) {
			//Debug.Log ("started coroutine for getting data");
			StartCoroutine (sendData.GetDataFromServer ());
		}
	}

	public void OnFirstAccelerate() {
		if (!MoveCar.isControlledByAI) {
			StartCoroutine (sensors.addInformationList ());
		}
	}
	
	public void Update() {
		//This is expensive but we do it only once..
		if (!isFinished) {
			mySpeed = rb.velocity.magnitude * 3.6f;
			scaledSpeed = Map (0, maxSpeed, 0f, 1f, mySpeed);

			if (!isControlledByAI) {
				float moveVertical = Input.GetAxisRaw ("Vertical");
				float moveHorizontal = Input.GetAxisRaw ("Horizontal");
				//Converting input to output in game
				
				/*ACCELERATE/BRAKE DATA*/
				if (moveVertical == 1) {
					isAccelerating = 1f;
					if (!begunAccelerating) {
						OnFirstAccelerate ();
						begunAccelerating = true;
					}
				} else if (moveVertical <= 0) {
					isAccelerating = 0f;
				}

				/*TURNING DATA*/
				if (moveHorizontal == 1) {
					isTurningLeft = 0f;
					isTurningRight = 1f;
					isNotTurning = 0f;
				} else if (moveHorizontal == 0) {
					isTurningLeft = 0f;
					isTurningRight = 0f;
					isNotTurning = 1f;
				} else if (moveHorizontal == -1) {
					isTurningLeft = 1f;
					isTurningRight = 0f;
					isNotTurning = 0f;
				}
				//Debug.Log("(user input) A: " + isAccelerating + " D: " + isDecelerating + " B: " + isBraking);
			} 
			//Converting AI output to game output
			else {
				//Moving.. (back and forth)
				if (shouldAccelerate == 1) {
					isAccelerating = 1f;
					//isBraking = 0f;
					//This is AI begunaccelerate
					if (!begunAccelerating) {
						OnFirstAccelerate ();
						begunAccelerating = true;
					}
				} else if (shouldAccelerate == 0) {
					isAccelerating = 0f;
				}

				//Turning...
				if (shouldTurnLeft == 1) {
					isTurningLeft = 1f;
					isTurningRight = 0f;
					isNotTurning = 0f;
				} else if (shouldTurnRight == 1) {
					isTurningLeft = 0f;
					isTurningRight = 1f;
					isNotTurning = 0f;
				} else if (shouldNotTurn == 1) {
					isTurningLeft = 0f;
					isTurningRight = 0f;
					isNotTurning = 1f;
				}
				//This will be changed when we have a neural network for turning
			}

			GetComponent<AudioSource> ().clip = movingCarSound;
			//If we are moving too fast then set acceleration to 0
			PlaySound ();
		}
	}

	//Being called from Sensors..
	public void IsFinished(bool _crashed) {
		isFinished = true;
		crashed = _crashed;

		//If we crashed and human is controlling then don't stop.
		if (crashed) {
			finishText.text = "Crashed";
			sensors.ClearList ();
			StartCoroutine(RestartIn(1f));
		} else {
			finishText.text = "Finished";
			StartCoroutine(LoadLevel("Finished", 1f));
		}
	}

	public IEnumerator LoadLevel(string levelName, float waitTime) {
		yield return new WaitForSeconds (waitTime);
		Application.LoadLevel (levelName);
	}

	//instead of this wait for request
	public IEnumerator RestartIn(float waitTime) {
		yield return new WaitForSeconds(waitTime);
		StartAgain ();
	}

	private void PlaySound() {
		if (isAccelerating == 1) {
			//slowly turn on engine sound
			audioSource.volume = Mathf.Lerp(audioSource.volume, 1, 0.1f);
		} 
		else {
			//slowly turn off engine sound
			audioSource.volume = Mathf.Lerp(audioSource.volume, 0, 0.1f);
		}

		if (!audioSource.isPlaying) {
			audioSource.Play ();
		}
	}

	public void FixedUpdate() {
		if (!isFinished) {
			float motor = maxMotorTorque * isAccelerating;
			float brake = maxBrakeTorque * (1-isAccelerating); 

			//Maps current speed from 1 to 0.5f
			//This makes it harder to turn at faster speeds
			float mappedSpeed = Map (0, maxSpeed, 1f, 0.3f, mySpeed);

			float steering = 0f;
			if (isTurningLeft > 0) {
				steering = maxSteeringAngle * -isTurningLeft * mappedSpeed;
			} else if (isTurningRight > 0) {
				steering = maxSteeringAngle * isTurningRight * mappedSpeed;
			} else if (isNotTurning > 0) {
				steering = 0;
			}

			//my speed goes above max speed sometimes so we need to fix that later on...
			if (mySpeed > maxSpeed && motor > 0) {
				motor = 0;
			}

			foreach (AxleInfo axleInfo in axleInfos) {
				if (axleInfo.steering) {
					axleInfo.leftWheel.steerAngle = steering;
					axleInfo.rightWheel.steerAngle = steering;
				}
				if (axleInfo.motor) {
					axleInfo.leftWheel.motorTorque = motor;
					axleInfo.rightWheel.motorTorque = motor;
				}
				if (axleInfo.braking) {
					axleInfo.leftWheel.brakeTorque = brake;
					axleInfo.rightWheel.brakeTorque = brake;
				}
			}
		}
	}

	public float Map(float OldMin, float OldMax, float NewMin, float NewMax, float OldValue) {
		float OldRange = (OldMax - OldMin);
		float NewRange = (NewMax - NewMin);
		float NewValue = (((OldValue - OldMin) * NewRange) / OldRange) + NewMin;
		
		if (NewValue < NewMin) {
			return NewMin;
		}
		if (NewValue > NewMax) {
			return NewMax;
		}
		return NewValue;
	}
}

//Array of [{f, l, r, iA, iB, iL, iR, iS})
//Is turning right
//Is turning left
//Is turning

//Variables for each wheel
[System.Serializable]
public class AxleInfo {
	public WheelCollider leftWheel;
	public WheelCollider rightWheel;
	public bool motor; // is this wheel attached to motor?
	public bool steering; // does this wheel apply steer angle?
	public bool braking;
}
