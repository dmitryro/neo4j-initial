import logging
import neo4j
from neo4j import GraphDatabase, basic_auth
from neo4j import Query
from utils import read_env, encode

logger = logging.getLogger(__name__)
uri = "neo4j://neo4j:7687"
driver = GraphDatabase.driver(uri, auth=basic_auth("user", "pass"), encrypted=False, max_connection_lifetime=3600, trust=neo4j.TRUST_ALL_CERTIFICATES)

def create_question_index(tx, question):
    """ Create a question """
    tx.run("CREATE INDEX ON :Question(question)")


def search_answer(tx, question):
    """ Search for an answer """
    label = encode(question)
    #result = tx.run("MATCH (q:Question) WHERE q.label = $label return q.answer AS answer", label=label)
    with driver.session() as session:
        result = session.run(Query("MATCH (q: Question) WHERE apoc.text.levenshteinDistance($question, q.question) < 3.1 return q.answer AS answer", timeout=1.0), question=question)
        return list(result)[0]['answer']
    return None


def search_question(tx, answer):
    """ Search for a question """
    with driver.session() as session:
        result = session.run(Query("MATCH (q: Question) WHERE apoc.text.levenshteinDistance($answer, q.answer) < 3.1 return q.question AS question", timeout=1.0), answer=answer)
        return list(result)[0]['question']
    return None


def initiate_indexes():
    """ Initialize any indexes """
    try:
        driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "graph"), encrypted=False, max_connection_lifetime=3600, trust=neo4j.TRUST_ALL_CERTIFICATES)
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
        driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "graph"), encrypted=False, max_connection_lifetime=3600, trust=neo4j.TRUST_ALL_CERTIFICATES)

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
        driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "graph"), encrypted=False, max_connection_lifetime=3600, trust=neo4j.TRUST_ALL_CERTIFICATES)

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
        driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "graph"), encrypted=False, max_connection_lifetime=3600, trust=neo4j.TRUST_ALL_CERTIFICATES)
        with driver.session() as session:
            q = session.write_transaction(edit_existing_question, question, answer)
    except Exception as e:
        logger.info(f"Failed connecting to bolt - {e}")
    return q


def add_question(question=None, answer=None):
    """ Add a new question to the KB """
    try:
        driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "graph"), encrypted=False, max_connection_lifetime=3600, trust=neo4j.TRUST_ALL_CERTIFICATES)

        with driver.session() as session:
            session.write_transaction(create_new_question, question, answer)
    except Exception as e:
        logger.info(f"Failed connecting to bolt - {e}")


def add_related_question(question, related):
    """ Add a related question to the KB """
    try:
        driver = GraphDatabase.driver(uri, auth=basic_auth("neo4j", "graph"), encrypted=False, max_connection_lifetime=3600, trust=neo4j.TRUST_ALL_CERTIFICATES)

        with driver.session() as session:
            session.write_transaction(create_new, question, answer)
            session.write_transaction(add_related, question, related)
    except Exception as e:
        logger.info(f"Failed connecting to bolt - {e}")
