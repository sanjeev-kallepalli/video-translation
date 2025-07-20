base_prompt = [
    {
      "role": "system",
      "content": [
        {
          "type": "input_text",
          "text": "You are intelligent advisor who assign the timestamps given in user's inputs."
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "You will receive two texts. One with the timestamps at the end of sentence and the other without the timestamp.\n\nThe sentence without the timestamp is to be returned with assigned timestamps given as input.\n\n"
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "This is for majestic sauce. First the protein 16 ohms in the prior. 0.0 6.0\nOil. 12.0 13.0\nLet's oil. Not so much. 16.0 18.0\nAdd curry leaves. 21.0 22.0\nActually 2. 27.0 28.0\nGinger garlic. 31.0 33.0\nThank you for the help. 36.0 38.0\nIt's very spicy on me. 38.0 39.0\nIt's not as good. 39.0 40.0\nIt's the order you can find the add extra of green chili. 40.0 43.0\nIf it's not as spicy, go not green chili. 52.0 55.0\nAdd half ladder. 56.0 58.0\nAdd half ladder. 58.0 59.0\nAdd half ladder. 59.0 60.0\nOh, today's sauce. 60.0 62.0\nI'm going to add 1 ladder. 68.0 70.0\nAnd mix. 72.0 73.0\nHalf ladder of the water. 80.0 82.0\nAnd mix. 86.0 87.0\nThese are also of lies for apologies. 94.0 96.0\nThis also a little bit thick. 107.0 109.0\nLet it cook on the little bit thick. 109.0 111.0\nSo when it starts boiling, you can add the protein. 112.0 116.0\nThis recipe applies for vanilla majestic, Apollo fish and chicken majestic. 120.0 125.0\nOnce it's boiled, you can add the protein. 132.0 134.0\nIt's very good. 134.0 136.0\nAdd the curry leaves. 142.0 144.0\nAdd the curry leaves. 149.0 151.0\n\nThis is for majestic sauce\nFirst the protein, 16oz in the fryer\nOil\nAdd curry leaves\nDry chili too\nGinger garlic\nIf the order is spicy, add extra green chili\nIf it's not spicy, don't add green chili\nAdd half ladle of kadai sauce\nApollo sauce, one and a half ladle\nAnd mix\nHalf ladle of the water\nAnd mix\nThis sauce also applies for Apollo fish\nLet it cook until it gets a little bit thicker\nSo when it starts boiling, you can add the protein\nThis recipe applies for paneer majestic, Apollo fish, and chicken majestic\nOnce it's boiling, you can add the protein\nAdd the coriander"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Here are the sentences with the assigned timestamps:\n\nThis is for majestic sauce. 0.0 3.0\nFirst the protein, 16oz in the fryer. 3.0 6.0\nOil. 12.0 13.0\nLittle oil. Not so much. 16.0 18.0\nAdd curry leaves. 21.0 22.0\nDry chili too. 27.0 28.0\nGinger garlic. 31.0 33.0\nIf the order is spicy, add extra green chili. 40.0 43.0\nIf it's not spicy, don't add green chili. 52.0 55.0\nAdd half ladle of kadai sauce. 56.0 58.0\nApollo sauce, one and a half ladle. 68.0 70.0\nAnd mix. 72.0 73.0\nHalf ladle of the water. 80.0 82.0\nAnd mix. 86.0 87.0\nThis sauce also applies for Apollo fish. 94.0 96.0\nLet it cook until it gets a little bit thicker. 109.0 111.0\nSo when it starts boiling, you can add the protein. 112.0 116.0\nThis recipe applies for paneer majestic, Apollo fish, and chicken majestic. 120.0 125.0\nOnce it's boiling, you can add the protein. 132.0 134.0\nAdd the coriander. 134.0 136.0\nAdd the curry leaves. 142.0 144.0\nAdd the curry leaves. 149.0 151.0"
        }
      ]
    }
]

healthcare_extraction_prompt = """
You are a medical assistant tasked with extracting healthcare-related information from a conversation transcript. Your goal is to identify and categorize key details about the patient's condition, demographics, medical history, potential diagnosis, next steps, and any prescriptions discussed.
You will receive a conversation transcript as input, and you need to return a structured JSON response containing

the following sections:

Classify the following:
1. Symptoms / Complaints (with description, location, severity, duration)
2. Patient Demographics (age, gender)
3. Medical History (conditions, medications, allergies if mentioned)
4. Potential Diagnosis (based on what’s discussed, even if not confirmed)
5. Next Steps / Follow-up (tests suggested, next visit)
6. Prescriptions / Treatment (if discussed)

If any section is not mentioned, return it as empty or with `"Not discussed"`.
If you find any medical jargon or terms, ensure they are correctly interpreted and included in the JSON.
if the conversation is not related to healthcare or no text, return an empty JSON object.
Do not halucinate or provide any additional commentary, just provide the information that is present in the conversation.

### Example Transcript:
```
D: What brought you in today?
P: Sure, I'm I'm just having a lot of chest pain and and so I thought I should get it checked out.
D: OK, before we start, could you remind me of your gender and age? 
P: Sure 39, I'm a male.
D: OK, and so when did this chest pain start?
P: It started last night, but it's becoming sharper.
D: OK, and where is this pain located? 
P: It's located on the left side of my chest.
D: OK, and, so how long has it been going on for then if it started last night?
P: So I guess it would be a couple of hours now, maybe like 8.
D: OK. Has it been constant throughout that time, or uh, or changing? 
P: I would say it's been pretty constant, yeah.
D: OK, and how would you describe the pain? People will use words sometimes like sharp, burning, achy. 
P: I'd say it's pretty sharp, yeah.
D: Sharp OK. Uh, anything that you have done tried since last night that's made the pain better?
P: Um not laying down helps.
```
### Return the response in the following JSON format:
```
{
  "symptoms": [
    {
      "primary complaint": "chest pain",
      "location": "left side of chest",
      "severity": "sharp",
      "duration": "8 hours",
      "progression": "becoming sharper",
      "frequency": "constant",
      "factors": "laying down helps"
    }
  ],
  "demographics": {
    "age": 39,
    "gender": "male"
  },
  "medical_history": {
    "conditions": "Not discussed",
    "medications": "Not discussed",
    "allergies": "Not discussed"
  },
  "potential_diagnosis": [
    "not specified"
  ],
  "next_steps": {
    "tests": ["Not discussed"],
    "follow_up": "Not scheduled yet"
  },
  "prescriptions": ["not discussed"]
}
```
below is the user input:
user-input:{query}
"""