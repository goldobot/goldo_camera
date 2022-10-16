#include <errno.h>
#include <fcntl.h> 
#include <string.h>
#include <unistd.h>
#include <zmq.h>
#include <math.h>
#include <pthread.h>
#include <string.h>

int main(int argc, char **argv)
{
  void* m_zmq_context = zmq_init(1);

  void* m_detect_socket = zmq_socket(m_zmq_context, ZMQ_SUB);
  if (m_detect_socket<0) {
    printf ("Cannot create ZMQ_SUB socket\n");
    return -1;
  }

  int rc = zmq_connect(m_detect_socket, "tcp://127.0.0.1:3202");
  if (rc<0) {
    printf ("Cannot connect to 127.0.0.1:3202\n");
    return -1;
  }
  printf ("zmq_connect() DONE\n");
  zmq_setsockopt(m_detect_socket,ZMQ_SUBSCRIBE, "", 0);

  zmq_pollitem_t poll_items[1];

  poll_items[0].socket = m_detect_socket;
  poll_items[0].fd = 0;
  poll_items[0].events = ZMQ_POLLIN;

  while(true)
  {
    zmq_poll (poll_items, 1, 100);

    if(poll_items[0].revents && ZMQ_POLLIN)
    {            
      unsigned char buff[1024];
      size_t bytes_read = 0;
      int64_t more=1;
      size_t more_size = sizeof(more);
      while(more)
      {
        bytes_read += zmq_recv(m_detect_socket, buff + bytes_read, sizeof(buff) - bytes_read, 0);           
        zmq_getsockopt(m_detect_socket, ZMQ_RCVMORE, &more, &more_size);
      }

      //printf ("bytes_read=%d\n", (int)bytes_read);
      if (bytes_read==16)
      {
        int *buff_i = (int *)buff;
        char color_s[16];
        if ((unsigned int)buff_i[1]==1)
        {
          strncpy(color_s,"RED  :",16);
        }
        else if ((unsigned int)buff_i[1]==2)
        {
          strncpy(color_s,"GREEN:",16);
        }
        else
        {
          strncpy(color_s,"?????:",16);
        }
        printf ("%s <%d,%d>\n\n", color_s, buff_i[2], buff_i[3]);
      }
    }

    sched_yield();
  }

  return 0;
}
