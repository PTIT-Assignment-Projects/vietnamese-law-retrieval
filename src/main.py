from src.evaluation.evaluator_service import EvaluatorService
from src.search_engine import SearchEngine
from src.util import constant


def main():
    # query = 'Tổ chức khoa học và công nghệ có thể được chia thành một số tổ chức khoa học và công nghệ, AND quy định'
    # method = constant.VSM_MODEL_NAME
    search_engine = SearchEngine()
    # search_engine._build_index()
    search_engine.load_prebuilt_index()
    # results = search_engine.search(query, method)
    # search_engine.display_results(results, query, method)


    # evaluator_service = EvaluatorService(search_engine)
    # evaluator_service.load_ground_truth()
    # evaluator_service.run_evaluation_and_save()
if __name__ == "__main__":
    main()