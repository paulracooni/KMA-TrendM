from time import sleep, time
from itertools import chain

import numpy as np

from models import News, NewsDB, Embedding
from modules.news_gpt import ChatGPT
from utils.logger import DbLogger

logger = DbLogger(__name__.split(".")[-1])

class Deduplicator:

    def __init__(self, th=0.9):
        self.th = th

    def __call__(self, news_ids):
        if any([isinstance(ids, list) for ids in news_ids]):
            news_ids = list(chain.from_iterable(news_ids))
        logger.info(f"Input ids={len(news_ids)}", not_db=True)
        
        embeddings = self.gen_embeddings(news_ids=news_ids)
        logger.info(f"Deduplicator.embeddings={len(embeddings)}", not_db=True)

        groups = self.grouping(embeddings)
        logger.info(f"Deduplicator.grouping={len(groups)}", not_db=True)

        exclude_ids = self.gen_exclude_ids(groups)
        logger.info(f"Deduplicator.exclude_ids={len(exclude_ids)}", not_db=True)

        news_ids = list(set(news_ids) - set(exclude_ids))
        logger.info(f"Deduplicator.news_ids={len(news_ids)}", not_db=True)
        return news_ids

    def gen_embeddings(self, news_ids):

        embeddings = dict()
        q_news = News.select().where(News.id << news_ids)
        for i, news in enumerate(q_news):

            q_emb = Embedding.select().where(Embedding.input == news.title)
            if q_emb.exists():
                embeddings[news.id] = q_emb.get().vector

            else:
                st = time()
                vector, usage = ChatGPT.as_vector_and_usage(
                    ChatGPT.embedding(news.title, as_vector=False))
                
                embeddings[news.id] = vector

                with NewsDB._meta.database.atomic():
                    Embedding.create(
                        model  = ChatGPT.emb_model,
                        vector = vector,
                        input  = news.title,        )

                logger.info(data=dict(
                    news_id=news.id, usage=usage, exec_time=time()-st))

            if i % 10 == 0:
                logger.info(
                    f"Deduplicator.embeddings progress "
                    f"[{i}/{len(q_news)}][{(i/len(q_news))*100:.2f}%]", not_db=True)

        return embeddings
    
    def grouping(self, embeddings):
        cos_sim = lambda a, b: np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))

        groups = dict()
        keys = list(embeddings.keys()) # key is news_id
        for i, ik in enumerate(keys):
            for j, jk in enumerate(keys):
                if j <= i : continue
                is_similar = cos_sim(embeddings[ik], embeddings[jk]) > self.th and ik != jk
                i_news, j_news     = News.get_by_id(ik), News.get_by_id(jk)
                is_same_title      = i_news.title       == j_news.title
                is_same_url        = i_news.url         == j_news.url
                is_same_url_origin = i_news.url_origin  == j_news.url_origin
                if is_similar or is_same_title or is_same_url or is_same_url_origin:
                    exist_group = False
                    for gk, group in groups.items():
                        if ik in group or jk in group:
                            groups[gk] = list(set(group).union(set([ik, jk])))
                            exist_group = True
                            break

                    if not exist_group:
                        groups[len(groups)] = [ik, jk]
        return groups

    def gen_exclude_ids(self, groups):
        exclude_ids = []
        for _, group in groups.items():
            selected_id = group[np.argmax([
                len(News.select().where(News.id == id).get().article)
                for id in group
            ])]
            for id in group:
                if selected_id != id:
                    exclude_ids.append(id)
        return exclude_ids