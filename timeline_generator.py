""" 
This file runs the LLM and image generation model responsible in forming the visual timeline data.
"""

import os
import re
import time
import openai
from langchain import PromptTemplate, LLMChain, OpenAI


## Uncomment and enter API key from https://platform.openai.com/account/api-keys
# os.environ["OPENAI_API_KEY"] = "sk-####" 
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_timeline(year, hist_event):
    """ 
    Generates the captions and image prompt of each key event in a timeline.

    For LLM output, hallucinations was minimized by letting the model verify the legibility of input.
    """
    llm = OpenAI(
        model="gpt-3.5-turbo-instruct",
        temperature=0.5,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    prompt_template_name = PromptTemplate(
        input_variables = ["year","event"],
        template="""
        You are an expert historian and a visual storyteller.

        Generate 8 to 10 bullets narrating the key events that happened in the given historical event in chronological order. 
        You cannot return less than 8 bullets.

        Start your response with the headline for the historical event like this:
        Title: Columbus voyage to America

        After this, generate a list per key event, following this format:
        Caption: October 1492 - Columbus reaches the island of Guanahani in the Bahamas
        AI Prompt: Create an image of Columbus and his crew landing on the shores of Guanahani, greeted by curious indigenous people.

        Be informative with the caption and always add a date. 
        Be creative with the AI prompt description. Both should be concise. Again, there should be no less than 8 entries in the list.

        If the historical event input didn't really occur in the past, don't generate the list and instead say "This is not a historical event" 
        with a 1 sentence explanation of why it is so. However, if part of the historical event input is misunderstood or only the input year is 
        wrong, briefly explain why the input is wrong and still proceed with the generation of the list but with the correct events. 
        Don't add a closing statement at the end

        Here's the historical event year and description:
        {year} - {event}
        """
    )

    # NOTE - input token costs around $0.0004 while max output token costs $0.0041. See latest pricing in https://openai.com/pricing
    llm_chain = LLMChain(llm=llm, prompt=prompt_template_name, output_key="text_output")

    response = llm_chain({"year":year, "event":hist_event})
    return response


def generate_illustration_url(prompt):
    """ 
    Generates the illustration of each key event in a timeline using their text-to-image prompts.
    """
    # NOTE - generation of 256x256 image using DALL-E costs $0.016 with rate limit of 5 images/1 min (in free tier)
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="256x256",
    )
    
    image_url = response['data'][0]['url']
    return image_url


def get_timeline_infos(year, hist_event):
    """ 
    Collects the title, caption, and illustration urls of each key events in a given historical timeline
    However, if the input is invalid, also collect the error message containing the reasoning for invalid input.
    """
    # Generate captions and text-to-image prompts via LLM
    response = generate_timeline(
            year=year, 
            hist_event=hist_event
        )
    
    text_output = response["text_output"]
    non_empty_txt = [string for string in text_output.split('\n') if string]

    # Separate captions and image prompts
    caption_list=[]
    image_prompt_list=[]
    title=""
    error_message=""

    for response in non_empty_txt:
        caption_part = re.match("(.*)?Caption: (.*)", response)
        if caption_part:
            caption = caption_part.group(2)
            caption_list.append(caption)

        image_promt_part = re.match("(.*)?AI Prompt: (.*)", response)
        if image_promt_part:
            image_prompt = image_promt_part.group(2)
            image_prompt_list.append(image_prompt)

        title_part = re.match("(.*)?Title: (.*)", response)
        if title_part:
            title = title_part.group(2)

    # Generate illustrations from text-to-image prompts
    illustration_urls = []
    if len(image_prompt_list) != 0:
        for image_prompt in image_prompt_list:
            image_url = generate_illustration_url(prompt=image_prompt)
            illustration_urls.append(image_url)
            time.sleep(15) # Avoids the free tier rate limit of DALL-E API

        error_message = ""
    else:
        # Get first text output containing the explanation of invalid input
        error_message = non_empty_txt[0].strip()
        
    return title, caption_list, illustration_urls, error_message



