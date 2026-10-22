# 私房厨房的主厨二级认证：令牌由 SECRET_KEY 签名并带时间戳，服务端可验证、会过期
import logging

from django.conf import settings
from django.core import signing
from rest_framework import permissions

logger = logging.getLogger(__name__)

CHEF_TOKEN_SALT = "kitchen.chef"
CHEF_TOKEN_MAX_AGE = 7 * 24 * 3600  # 秒
CHEF_TOKEN_HEADER = "HTTP_X_CHEF_TOKEN"


def issue_chef_token() -> str:
    return signing.TimestampSigner(salt=CHEF_TOKEN_SALT).sign(settings.CHEF_USERNAME)


def is_valid_chef_token(token: str) -> bool:
    if not token:
        return False
    try:
        value = signing.TimestampSigner(salt=CHEF_TOKEN_SALT).unsign(token, max_age=CHEF_TOKEN_MAX_AGE)
    except signing.SignatureExpired:
        logger.info("chef token expired")
        return False
    except signing.BadSignature:
        logger.warning("chef token rejected: bad signature")
        return False
    return value == settings.CHEF_USERNAME


def request_has_chef_token(request) -> bool:
    return is_valid_chef_token(request.META.get(CHEF_TOKEN_HEADER, ""))


class IsChef(permissions.BasePermission):
    """请求头 X-Chef-Token 带有效的主厨令牌。"""

    def has_permission(self, request, view):
        return request_has_chef_token(request)
