import { OpenAI } from "openai";
import pinecone from "./pinecone";
import { v4 as uuidv4 } from "uuid";

// Init OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

const indexName = process.env.PINECONE_INDEX_NAME!;
const namespace = "default"; // Or customize if needed

export async function embedAndUpload(docText: string, docName: string) {
  // 1. Chunk the document
  const chunkSize = 500;
  const overlap = 50;
  const words = docText.split(" ");
  const chunks: string[] = [];

  for (let i = 0; i < words.length; i += chunkSize - overlap) {
    const chunk = words.slice(i, i + chunkSize).join(" ");
    if (chunk.length > 0) chunks.push(chunk);
  }

  // 2. Embed chunks
  const embeddings = await Promise.all(
    chunks.map(async (chunk) => {
      const response = await openai.embeddings.create({
        input: chunk,
        model: "text-embedding-3-small"
      });
      return response.data[0].embedding;
    })
  );

  // 3. Prepare vectors
  const vectors = chunks.map((chunk, i) => ({
    id: uuidv4(),
    values: embeddings[i],
    metadata: {
      text: chunk,
      chunk_index: i,
      doc_name: docName
    }
  }));

  // 4. Upsert to Pinecone
  const pineconeIndex = pinecone.Index(indexName);
  await pineconeIndex.upsert(vectors, namespace);

  return { success: true, chunksUploaded: vectors.length };
}
