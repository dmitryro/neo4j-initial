from neo4j import GraphDatabase
from utils import read_env, encode


def create_question_index(tx, question):
    """ Create a question """
    tx.run("CREATE INDEX ON :Question(question)")


def search_answer(tx, question):
    """ Search for an answer """
    label = encode(question)
    result = tx.run("MATCH (q:Question) WHERE q.label = $label return q.answer AS answer", label=label)
    try:
        return list(result)[0]['answer']
    except Exception as e:
        return None


def search_question(tx, answer):
    """ Search for a question """
    result = tx.run("MATCH (q:Question) WHERE q.answer = $answer return q.question AS question", answer=answer)
    try:
        return list(result)[0]['question']
    except Exception as e:
        return None


def initiate_indexes():
    """ Initialize any indexes """
    try:
        uri = read_env("BOLT_URI")
        driver = GraphDatabase.driver(uri, auth=("neo4j", "graph"))
        with driver.session() as session:
            answer = session.write_transaction(create_question_index, None)
            session.close()
        driver.close()

    except Exception as e:
        answ = None
    

def find_answer(question):
    """ Find an answer """
    try:
        answer = None
        uri = read_env("BOLT_URI")
        driver = GraphDatabase.driver(uri, auth=("neo4j", "graph"))

        with driver.session() as session:
            answer = session.read_transaction(search_answer, question)
            session.close()
        driver.close()
        return answer

    except Exception as e:
        answ = None
        print(f"Failed connecting to bolt - {e}")

    return answer


def find_question(answer):
    """ Find an answer """
    try:
        q = None
        uri = read_env("BOLT_URI")
        driver = GraphDatabase.driver(uri, auth=("neo4j", "graph"))

        with driver.session() as session:
            q = session.read_transaction(search_question, answer)
            session.close()
        driver.close()
        return q

    except Exception as e:
        q = None
        print(f"Failed connecting to bolt - {e}")

    return q


def extend_answer(question, index, addition):
    """ Extend an answer """
    answer = find_answer(question) 
    extend_at_position(answer, index, addition)


def extend_at_position(answer, index, addition):
    """ Extend an answer """
    pass


def edit_existing_question(tx, question, answer):
    result = tx.run("MATCH (q:Question{question:$question}) SET q.answer = $answer", question=question, answer=answer)
    return result


def create_new_question(tx, question, answer):
    """ Add new question """
    props = dict()
    props['props'] = {'question':question, 'answer': answer, 'label':encode(question)} 
    tx.run("UNWIND $props AS map CREATE (q:Question) SET q = map", props)


def add_related(tx, question, related):
    """ Add a related question to the KB """
    tx.run("MERGE (a:Question {question: $question}) "
           "MERGE (a)-[:RELATED_TO]->(related:Question {question: $related})",
           question=question, related=related)


def edit_question(question=None, answer=None):
    """ Add a new question to the KB """
    q = None
    try:
        uri = read_env("BOLT_URI")
        driver = GraphDatabase.driver(uri, auth=("neo4j", "graph"))
        with driver.session() as session:
            q = session.write_transaction(edit_existing_question, question, answer)
    except Exception as e:
        logger.info(f"Failed connecting to bolt - {e}")
    return q


def add_question(question=None, answer=None):
    """ Add a new question to the KB """
    try:
        uri = read_env("BOLT_URI")
        driver = GraphDatabase.driver(uri, auth=("neo4j", "graph"))

        with driver.session() as session:
            session.write_transaction(create_new_question, question, answer)
    except Exception as e:
        logger.info(f"Failed connecting to bolt - {e}")


def add_related_question(question, related):
    """ Add a related question to the KB """
    try:
        uri = read_env("BOLT_URI")
        driver = GraphDatabase.driver(uri, auth=("neo4j", "graph"))

        with driver.session() as session:
            session.write_transaction(create_new, question, answer)
            session.write_transaction(add_related, question, related)
    except Exception as e:
        logger.info(f"Failed connecting to bolt - {e}")
