from neo4j import GraphDatabase
from utils import read_env, encode

def create_question_index(tx):
    tx.run("CREATE INDEX ON :Question(question)")


def search_answer(tx, question):
    label = encode(question)
    result = tx.run("MATCH (q:Question) WHERE q.label = $label return q.answer AS answer", label=label)
    try:
        return list(result)[0]['answer']
    except Exception as e:
        return None

def find_answer(question):
    try:
        answer = None
        uri = "bolt://neo4j:7687"
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


def create_new_question(tx, question, answer):
    """ Add new question """
    props = dict()
    props['props'] = {'question':question, 'answer': answer, 'label':encode(question)} 
    tx.run("UNWIND $props AS map CREATE (q:Question) SET q = map", props)


def add_related(tx, question, related):
    tx.run("MERGE (a:Question {question: $question}) "
           "MERGE (a)-[:RELATED_TO]->(related:Question {question: $related})",
           question=question, related=related)


def add_question(question=None, answer=None):
    try:
        uri = "bolt://neo4j:7687"
        driver = GraphDatabase.driver(uri, auth=("neo4j", "graph"))

        with driver.session() as session:
            session.write_transaction(create_new_question, question, answer)
    except Exception as e:
        logger.info(f"Failed connecting to bolt - {e}")


def add_related_question(question, related):
    try:
        uri = "bolt://neo4j:7687"
        driver = GraphDatabase.driver(uri, auth=("neo4j", "graph"))

        with driver.session() as session:
            session.write_transaction(create_new, question, answer)
            session.write_transaction(add_related, question, related)
    except Exception as e:
        logger.info(f"Failed connecting to bolt - {e}")
