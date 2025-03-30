from functools import wraps
from typing import Callable

def with_testset_callbacks(callback: Callable[[str, dict], None]):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from inspect import signature, BoundArguments

            sig: BoundArguments = signature(fn).bind(*args, **kwargs)
            sig.apply_defaults()

            knowledge_base = sig.arguments.get("knowledge_base")
            
            if "num_questions" in kwargs:
                num_questions = kwargs["num_questions"]
                print(f"DEBUG: Using num_questions from kwargs: {num_questions}")
            else:
                num_questions = sig.arguments.get("num_questions", 120)
                print(f"DEBUG: Using num_questions from signature: {num_questions}")
                
            # Apply same pattern for language and agent_description
            if "language" in kwargs:
                language = kwargs["language"]
                print(f"DEBUG: Using language from kwargs: {language}")
            else:
                language = sig.arguments.get("language", "en")
                print(f"DEBUG: Using language from signature: {language}")
                
            if "agent_description" in kwargs:
                agent_description = kwargs["agent_description"]
                print(f"DEBUG: Using agent_description from kwargs: {agent_description}")
            else:
                agent_description = sig.arguments.get("agent_description", "")
                print(f"DEBUG: Using agent_description from signature: {agent_description}")
                
            question_generators = sig.arguments.get("question_generators", None)

            if question_generators is None:
                from giskard.rag.question_generators import (
                    simple_questions,
                    complex_questions,
                    distracting_questions,
                    situational_questions,
                    double_questions,
                    conversational_questions,
                )
                question_generators = [
                    simple_questions,
                    complex_questions,
                    distracting_questions,
                    situational_questions,
                    double_questions,
                    conversational_questions,
                ]
                

            if not isinstance(question_generators, (list, tuple)):
                question_generators = [question_generators]

            total_questions = num_questions
            print(f"DEBUG: total_questions set to: {total_questions}")
            print(f"DEBUG: Number of generators: {len(question_generators)}")
            
            # Print how questions will be distributed
            generator_num_questions = [
                total_questions // len(question_generators) + (1 if i < total_questions % len(question_generators) else 0)
                for i in range(len(question_generators))
            ]
            print(f"DEBUG: Distribution of questions per generator: {generator_num_questions}")
            
            callback("start_generation", {
                "num_questions": total_questions,
                "language": language,
                "agent_description": agent_description,
                "generators": [g.__class__.__name__ for g in question_generators],
            })

            # Patch the generator
            original_generate_questions = {}
            question_counter = 0

            for gen in question_generators:
                original_generate_questions[gen] = gen.generate_questions

                # Fix closure issue by creating a function that correctly captures gen_func
                def create_wrapper(gen_func):
                    def wrapped(*g_args, **g_kwargs):
                        nonlocal question_counter
                        
                        # Ensure the generator gets the correct number of questions 
                        # Don't let it be overridden by defaults
                        print(f"DEBUG: Generator kwargs before: {g_kwargs}")
                        
                        # Force the generator to use our num_questions
                        g_kwargs["num_questions"] = generator_num_questions[min(question_generators.index(gen), len(generator_num_questions)-1)]
                        
                        # Also ensure language and agent_description are passed correctly
                        g_kwargs["language"] = language
                        g_kwargs["agent_description"] = agent_description
                        
                        print(f"DEBUG: Generator kwargs after: {g_kwargs}")
                            
                        for q in gen_func(*g_args, **g_kwargs):
                            question_counter += 1
                            callback("question_generated", {
                                "question": q.question,
                                "position": question_counter,
                                "total_questions": total_questions
                            })
                            yield q
                    return wrapped

                gen.generate_questions = create_wrapper(gen.generate_questions)
            
            result = fn(*args, **kwargs)
            print(f"DEBUG: Final question count: {len(result.samples)}")

            for gen, orig in original_generate_questions.items():
                gen.generate_questions = orig

            callback("testset_ready", {"total_questions": len(result.samples)})
            return result

        return wrapper
    return decorator