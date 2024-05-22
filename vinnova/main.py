"""Main entry point for the Vinnova data project.

"""
from vinnova_drl import build_vinnova_drl_func, VinnovaDataRetrievalLayer
from llm import SemanticEngine, get_openai_client


VINNOVA_API_CONF_FILE = "vinnova_api_conf.json"


def main():
    vinnova_drl_func = build_vinnova_drl_func(VINNOVA_API_CONF_FILE)
    llm_client = get_openai_client()
    engine = SemanticEngine(
        client=llm_client,
        system_definition="You are the nice assistant brought forth by nice people to help with information.",
        llm_params={
            'model': 'gpt-4o',
            'temperature': 0.7,
            'max_tokens': 4096,
            'top_p': 1.0,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0,
            'n_completions': 1
        },
        tools=[vinnova_drl_func[api_key] for api_key in ['projekt-list', 'projekt-details']],
        respond_to_function=False
    )

    engine.process('I am researching Vinnova projects. I am curious about projects active in 2023 or later. Can you list them?')
    print(engine.message_stack)
    engine.process('I want detailed information on the Vinnova project "2023-02723".')
    print(engine.message_stack)


if __name__ == '__main__':
    main()
