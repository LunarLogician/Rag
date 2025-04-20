// app/api/embed/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { OpenAIEmbeddings } from '@langchain/openai';
import { PineconeStore } from '@langchain/community/vectorstores/pinecone'; // ✅ Correct now
import pinecone from '@/utils/pinecone';
import { v4 as uuidv4 } from 'uuid';


export async function POST(req: NextRequest) {
  const { text, namespace } = await req.json();

  if (!text || !namespace) {
    return NextResponse.json({ error: 'Missing text or namespace' }, { status: 400 });
  }

  try {
    const embeddings = new OpenAIEmbeddings({
      modelName: 'text-embedding-3-small',
      openAIApiKey: process.env.OPENAI_API_KEY,
    });    
    const index = pinecone.Index("embed-upload");

    const chunks = text.match(/(.|\s){1,2500}(\.|\s|$)/g)?.filter(Boolean) || [];

    const docs = chunks.map((chunk, i) => ({
      pageContent: chunk,
      metadata: {
        id: uuidv4(),
        namespace,
        chunkIndex: i,
        page_number: i + 1,
      },
    }));

    console.log(`Uploading ${docs.length} chunks to Pinecone under namespace "${namespace}"...`);

    await PineconeStore.fromDocuments(docs, embeddings, {
      pineconeIndex: index,
      namespace,
    });

    return NextResponse.json({ message: 'Uploaded to Pinecone' });
  } catch (error: any) {
    console.error('🔥 Pinecone upload error:', error.message, error);
    return NextResponse.json({ error: 'Embedding and upload failed' }, { status: 500 });
  }
}
