import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_real_ip = request.META.get("HTTP_X_REAL_IP")

    if x_real_ip:
        ip = x_real_ip.split(",")[0]
        logger.info(f"HTTP_X_REAL_IP: {ip}")
    else:
        ip = request.META.get("REMOTE_ADDR")
        logger.info(f"REMOTE_ADDR: {ip}")
    return ip
