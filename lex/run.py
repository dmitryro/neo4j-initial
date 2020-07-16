import aiotools
import asyncio
from neo4j import GraphDatabase

def create_new(tx, name):
    tx.run("CREATE (p:Person {name:$name}) RETURN p", name=name)
    
def add_liked(tx, name, liked_name):
    tx.run("MERGE (a:Person {name: $name}) "
           "MERGE (a)-[:LIKES]->(liked:Person {name: $liked_name})",

           name=name, liked_name=liked_name)

def add_person(name):
    try:
        uri = "bolt://neo4j:7687"
        driver = GraphDatabase.driver(uri, auth=("neo4j", "graph"))

        with driver.session() as session:
            session.write_transaction(create_new, name)
    except Exception as e:
        print(f"Failed connecting to bolt - {e}")


def add_liked_person(name, liked):
    try:
        uri = "bolt://neo4j:7687"
        driver = GraphDatabase.driver(uri, auth=("neo4j", "graph"))
        
        with driver.session() as session:
            session.write_transaction(create_new, name)
            session.write_transaction(add_liked, name, liked)
    except Exception as e:
        print(f"Failed connecting to bolt - {e}")


def main():
    try:
        uri = "bolt://neo4j:7687"
        driver = GraphDatabase.driver(uri, auth=("neo4j", "graph"))
       
        with driver.session() as session:     
            session.write_transaction(create_new, "Alice")

        with driver.session() as session:
            session.write_transaction(create_new, "Paul")

        with driver.session() as session:
            session.write_transaction(create_new, "Rob")

        with driver.session() as session:
            session.write_transaction(create_new, "Dmitry")

        with driver.session() as session:
            session.write_transaction(add_liked, "Alice", "Neo4j")
        with driver.session() as session:
            session.write_transaction(add_liked, "Rob", "Neo4j")
        driver.close()
    except Exception as e:
        print(f"Failed connecting to bolt - {e}")


def execute():
    print("Started...") 


async def echo(reader, writer):
   data = await reader.read(100)
   writer.write(data)
   await writer.drain()
   writer.close()


@aiotools.server
async def myworker(loop, pidx, args):
   server = await asyncio.start_server(echo, '0.0.0.0', 8888,
       reuse_port=True, loop=loop)
   print(f'[{pidx}] started')
   yield  # wait until terminated
   server.close()
   await server.wait_closed()
   print(f'[{pidx}] terminated')

if __name__ == '__main__':
   # Run the above server using 4 worker processes.
   main()
   aiotools.start_server(myworker, num_workers=4)
